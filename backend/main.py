"""
AMAZEBOT local LLM backend.

Bridges AMAZEBOT.html's Character Chat feature to a locally running Ollama
daemon, so persona chat works fully offline / without a Gemini API key.
Ollama must already be installed and running (see ../README.md).
"""

import glob
import os
import subprocess
import sys
import tempfile

import httpx
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, StreamingResponse
from pydantic import BaseModel

# Update this if `ollama list` prints a different tag after pulling the model.
MODEL_NAME = "LiquidAI/lfm2.5-1.2b-instruct"
OLLAMA_URL = "http://localhost:11434"
# Kept modest on purpose: this and num_ctx below both scale Ollama's KV-cache
# VRAM footprint during generation, and this machine's 6GB GPU has to share
# that headroom with the TTS model (tts_server.py) running at the same time —
# a wider context here was measured to squeeze TTS enough to make its own
# generation fall behind real-time playback (heard as the audio stalling).
HISTORY_TURNS_SENT = 8

# The voice-cloning model runs in its own process (tts_server.py), not here —
# see the comment at the top of that file for why: it has intermittently
# crashed the whole process outright (a native CUDA/cuDNN crash, not a normal
# exception), which must never be allowed to take down chat/transcription too.
TTS_SERVER_URL = "http://localhost:8001"
_tts_server_proc = None

# Teammate's GNN molecular-discovery service ("MD by AI" in the architecture
# diagram) — a separate repo/process we don't own or run. Its own app.py
# hardcodes port 8000, which collides with this backend, so it needs to be
# started on a different port (e.g. `uvicorn app:app --port 8002`) — that's
# a coordination point with the teammate, not something fixable from here.
MD_AI_URL = "http://localhost:8002"

VOICES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voices")
os.makedirs(VOICES_DIR, exist_ok=True)

app = FastAPI(title="AMAZEBOT Local LLM Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def ensure_tts_server_started():
    global _tts_server_proc
    if _tts_server_proc is not None and _tts_server_proc.poll() is None:
        return  # already running
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tts_server.py")
    _tts_server_proc = subprocess.Popen([sys.executable, script])


@app.on_event("startup")
async def on_startup():
    ensure_tts_server_started()


class HistoryTurn(BaseModel):
    role: str  # 'user' | 'ai'
    text: str


class PersonaChatRequest(BaseModel):
    persona_name: str
    system_prompt: str
    history: list[HistoryTurn] = []
    message: str
    max_tokens: int = 200
    num_ctx: int = 2048  # halved from 4096 — see HISTORY_TURNS_SENT comment above


def to_ollama_role(role: str) -> str:
    return "assistant" if role == "ai" else "user"


@app.get("/api/health")
async def health():
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{OLLAMA_URL}/api/tags")
            resp.raise_for_status()
            models = [m["name"] for m in resp.json().get("models", [])]
            return {
                "status": "ok",
                "ollama_running": True,
                "model_available": any(MODEL_NAME in m for m in models),
                "model": MODEL_NAME,
            }
    except httpx.HTTPError:
        return {
            "status": "ok",
            "ollama_running": False,
            "model_available": False,
            "model": MODEL_NAME,
        }


@app.post("/api/persona-chat")
async def persona_chat(req: PersonaChatRequest):
    messages = [{"role": "system", "content": req.system_prompt}]
    for turn in req.history[-HISTORY_TURNS_SENT:]:
        messages.append({"role": to_ollama_role(turn.role), "content": turn.text})
    messages.append({"role": "user", "content": req.message})

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{OLLAMA_URL}/api/chat",
                # keep_alive keeps the model resident in VRAM between chats — otherwise
                # Ollama unloads it after its default 5min idle window, forcing a slow reload.
                # num_predict caps reply length — keeps answers on-topic/concise instead of
                # rambling, and as a side effect shortens read-aloud synthesis time too.
                # Callers needing longer structured output (flashcards/quiz/design docs)
                # or bigger document context pass higher max_tokens/num_ctx explicitly.
                json={
                    "model": MODEL_NAME,
                    "messages": messages,
                    "stream": False,
                    "keep_alive": "30m",
                    "options": {"num_predict": req.max_tokens, "num_ctx": req.num_ctx},
                },
            )
    except httpx.ConnectError:
        return JSONResponse(
            status_code=503,
            content={"error": "Ollama is not running. Start it and try again."},
        )

    if resp.status_code != 200:
        return JSONResponse(
            status_code=502,
            content={"error": f"Ollama error: {resp.text}"},
        )

    data = resp.json()
    return {"response": data["message"]["content"], "model": MODEL_NAME}


# ── VOICE UPLOAD → SPEECH STYLE ──────────────────────────────────────────────
# CPU + int8 chosen deliberately: GPU transcription needs a full CUDA/cuBLAS
# toolkit install beyond just the GPU driver, and a "base" model on CPU already
# transcribes a short clip in ~1-2s, which is fast enough since this runs once
# per upload, not per chat turn.
_whisper_model = None

TONE_ANALYSIS_PROMPT = """Below is a transcript of someone talking. Write a short (2-4 sentence) speech-style guide describing HOW they talk: sentence length, vocabulary, slang, tone, filler words, pacing, and any verbal quirks. Do not describe what they said, only how they said it. Output only the style guide, nothing else.

Transcript:
\"\"\"{transcript}\"\"\"
"""


def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        _whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
    return _whisper_model


@app.post("/api/voice-to-tone")
async def voice_to_tone(file: UploadFile = File(...), persona_id: str = Form(None)):
    suffix = os.path.splitext(file.filename or "")[1] or ".wav"
    audio_bytes = await file.read()

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        model = get_whisper_model()
        segments, _ = model.transcribe(tmp_path)
        transcript = " ".join(seg.text for seg in segments).strip()
    except Exception as e:
        os.remove(tmp_path)
        return JSONResponse(status_code=500, content={"error": f"Transcription failed: {e}"})

    if not transcript:
        os.remove(tmp_path)
        return JSONResponse(status_code=422, content={"error": "Could not detect any speech in that recording."})

    # Keep the raw clip as this persona's voice reference for /api/read-aloud —
    # transcription alone (above) isn't enough, cloning needs the actual audio.
    if persona_id:
        for old in glob.glob(os.path.join(VOICES_DIR, f"{persona_id}.*")):
            os.remove(old)
        os.replace(tmp_path, os.path.join(VOICES_DIR, f"{persona_id}{suffix}"))
    else:
        os.remove(tmp_path)

    tone = ""
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{OLLAMA_URL}/api/chat",
                json={
                    "model": MODEL_NAME,
                    "messages": [{"role": "user", "content": TONE_ANALYSIS_PROMPT.format(transcript=transcript)}],
                    "stream": False,
                    "keep_alive": "30m",
                },
            )
            if resp.status_code == 200:
                tone = resp.json()["message"]["content"].strip()
    except httpx.HTTPError:
        pass  # fall through — frontend can still use the raw transcript

    return {"transcript": transcript, "tone": tone}


@app.post("/api/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """Fast speech-to-text only — no tone analysis, no sample saving. Used
    for turn-by-turn Voice Mode input, where /api/voice-to-tone (built for
    one-time character voice setup) would be doing unnecessary extra work
    on every single turn."""
    suffix = os.path.splitext(file.filename or "")[1] or ".webm"
    audio_bytes = await file.read()

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        model = get_whisper_model()
        segments, _ = model.transcribe(tmp_path)
        transcript = " ".join(seg.text for seg in segments).strip()
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Transcription failed: {e}"})
    finally:
        os.remove(tmp_path)

    return {"transcript": transcript}


@app.post("/api/add-voice-sample")
async def add_voice_sample(file: UploadFile = File(...), persona_id: str = Form(...)):
    """Adds an EXTRA reference clip for a character that already has a primary
    voice sample (from /api/voice-to-tone). No transcription here — this is
    purely for cloning accuracy: XTTS-v2 blends multiple reference clips into
    a more accurate voice print than a single short sample can give it."""
    if not glob.glob(os.path.join(VOICES_DIR, f"{persona_id}.*")):
        return JSONResponse(
            status_code=400,
            content={"error": "This character has no primary voice sample yet — upload one first."},
        )

    suffix = os.path.splitext(file.filename or "")[1] or ".wav"
    existing_extras = glob.glob(os.path.join(VOICES_DIR, f"{persona_id}__s*"))
    next_index = len(existing_extras) + 2  # primary sample is implicitly "1"

    audio_bytes = await file.read()
    out_path = os.path.join(VOICES_DIR, f"{persona_id}__s{next_index}{suffix}")
    with open(out_path, "wb") as f:
        f.write(audio_bytes)

    total_samples = len(glob.glob(os.path.join(VOICES_DIR, f"{persona_id}*")))
    return {"sample_count": total_samples}


# ── READ ALOUD — proxies to the isolated TTS microservice (tts_server.py) ───
# GPU only: confirmed via feasibility test this takes ~2-5s per reply on this
# machine's RTX 3060 once warm. CPU cloning would be far too slow to feel usable.
class ReadAloudRequest(BaseModel):
    persona_id: str
    text: str
    lang: str = "en"


@app.post("/api/read-aloud")
async def read_aloud(req: ReadAloudRequest):
    if not glob.glob(os.path.join(VOICES_DIR, f"{req.persona_id}*")):
        return JSONResponse(
            status_code=404,
            content={"error": "No voice recording saved for this character. Upload one when creating the character."},
        )

    try:
        async with httpx.AsyncClient(timeout=90) as client:
            resp = await client.post(
                f"{TTS_SERVER_URL}/synthesize",
                json={"persona_id": req.persona_id, "text": req.text, "lang": req.lang},
            )
    except httpx.ConnectError:
        # The TTS process isn't up — most likely it crashed (see tts_server.py's
        # docstring). Restart it so the *next* attempt has a chance of working,
        # rather than leaving Read Aloud permanently broken until a manual restart.
        ensure_tts_server_started()
        return JSONResponse(
            status_code=503,
            content={"error": "Voice service isn't responding (it may have crashed) — restarting it now, try again in about 30 seconds."},
        )

    if resp.status_code != 200:
        try:
            return JSONResponse(status_code=resp.status_code, content=resp.json())
        except Exception:
            return JSONResponse(status_code=502, content={"error": f"Voice service error: {resp.text[:200]}"})

    return Response(content=resp.content, media_type="audio/wav")


@app.post("/api/read-aloud-stream")
async def read_aloud_stream(req: ReadAloudRequest):
    """Streaming counterpart to /api/read-aloud — forwards chunks as the TTS
    service generates them instead of waiting for the whole clip, so Read
    Aloud/Voice Mode playback can start within a fraction of a second
    instead of after the full reply has finished synthesizing."""
    if not glob.glob(os.path.join(VOICES_DIR, f"{req.persona_id}*")):
        return JSONResponse(
            status_code=404,
            content={"error": "No voice recording saved for this character. Upload one when creating the character."},
        )

    async def proxy_chunks():
        try:
            async with httpx.AsyncClient(timeout=90) as client:
                async with client.stream(
                    "POST",
                    f"{TTS_SERVER_URL}/synthesize_stream",
                    json={"persona_id": req.persona_id, "text": req.text, "lang": req.lang},
                ) as resp:
                    async for chunk in resp.aiter_bytes():
                        yield chunk
        except httpx.ConnectError:
            ensure_tts_server_started()
            return

    return StreamingResponse(
        proxy_chunks(),
        media_type="application/octet-stream",
        headers={"X-Sample-Rate": "24000", "X-Channels": "1", "X-Format": "s16le"},
    )


# ── MOLECULE DISCOVERY — thin proxy to the teammate's "MD by AI" GNN service ─
# No LLM logic here on purpose — turning the user's chat message into this
# request shape happens client-side (AMAZEBOT.html), same as every other
# feature. This endpoint only exists to dodge the browser CORS block, since
# the teammate's FastAPI app has no CORSMiddleware configured.
class DiscoverMaterialRequest(BaseModel):
    # Matches the teammate's CVAE-based /api/discover DiscoveryRequest exactly
    # (their model requires all 9 fields, no defaults — we keep defensive
    # defaults on our side so an incomplete LLM extraction degrades gracefully
    # instead of a hard 422).
    seed_smiles: str = "CCO"
    target_gap: float = 2.0
    min_solubility: float = -2.0
    max_toxicity: float = 20.0
    dipole_moment: float = 1.5
    electron_affinity: float = 1.0
    polarizability: float = 80.0
    ionization_potential: float = 9.0
    hardness: float = 4.0
    electrophilicity: float = 2.0


@app.post("/api/discover-material")
async def discover_material(req: DiscoverMaterialRequest):
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(f"{MD_AI_URL}/api/discover", json=req.model_dump())
    except httpx.ConnectError:
        return JSONResponse(
            status_code=503,
            content={"error": f"MD-by-AI service isn't reachable at {MD_AI_URL}. Ask your teammate to start it (uvicorn app:app --port 8002)."},
        )

    if resp.status_code != 200:
        return JSONResponse(status_code=502, content={"error": f"MD-by-AI service error: {resp.text[:300]}"})

    return resp.json()
