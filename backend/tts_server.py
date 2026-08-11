"""
AMAZEBOT voice-cloning (TTS) microservice.

Isolated into its own process on purpose: loading XTTS-v2's CUDA/cuDNN
dependencies has intermittently crashed the whole Python process outright
(not a catchable exception — a native crash) on this machine. Keeping it in
a separate OS process means that crash can only take down Read Aloud/Voice
Mode, never chat, transcription, or summarization in the main backend
(main.py).
"""

import glob
import os
import sys
import tempfile
from collections import OrderedDict

os.environ.setdefault("COQUI_TOS_AGREED", "1")

if sys.platform == "win32":
    _torch_lib = os.path.join(os.path.dirname(sys.executable), "Lib", "site-packages", "torch", "lib")
    if os.path.isdir(_torch_lib):
        os.add_dll_directory(_torch_lib)

import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, StreamingResponse
from pydantic import BaseModel

VOICES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voices")
OUTPUT_SAMPLE_RATE = 24000  # fixed by XTTS-v2's hifigan decoder

app = FastAPI(title="AMAZEBOT TTS Service")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_tts_model = None
_xtts = None  # raw TTS.tts.models.xtts.Xtts instance, unwrapped from the TTS.api.TTS convenience wrapper

# gpt_cond_latent + speaker_embedding are the expensive-to-compute "voice print"
# derived from a persona's reference clip(s). Computing them is most of the
# latency of a single synthesis call, but they don't change unless the
# underlying sample files do — so cache them per persona, invalidated only
# when the sample file list/mtimes for that persona actually change.
#
# Bounded + LRU-evicted on purpose: each entry holds GPU tensors, and this
# process's GPU (a 6GB laptop card) has no room to keep every character ever
# used resident forever — an earlier unbounded version of this cache quietly
# ate ~4GB of VRAM over a long session of testing many characters, which
# starved the model of working memory and made generation itself fall behind
# real-time (heard as the audio repeatedly stalling, not clicking).
MAX_CACHED_VOICES = 8
_latents_cache: "OrderedDict[str, tuple[tuple, object, object]]" = OrderedDict()


class SynthesizeRequest(BaseModel):
    persona_id: str
    text: str
    lang: str = "en"  # XTTS-v2 supports: en es fr de it pt pl tr ru nl cs ar zh-cn hu ko ja hi


def get_tts_model():
    global _tts_model, _xtts
    if _tts_model is None:
        from TTS.api import TTS
        _tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cuda")
        _xtts = _tts_model.synthesizer.tts_model
    return _tts_model


def get_speaker_samples(persona_id: str) -> list[str]:
    # Primary sample is saved as "<persona_id>.<ext>" (from /api/voice-to-tone);
    # extra samples added later are "<persona_id>__s2.<ext>", "__s3", etc.
    # Passing multiple reference clips to XTTS-v2 gives it more voice data to
    # condition on, which generally improves cloning fidelity over one clip.
    return sorted(glob.glob(os.path.join(VOICES_DIR, f"{persona_id}*")))


def get_conditioning(persona_id: str, speaker_wavs: list[str]):
    """Returns (gpt_cond_latent, speaker_embedding) for a persona's voice,
    computing them once and reusing on every subsequent call for that same
    set of reference clips."""
    signature = tuple((f, os.path.getmtime(f)) for f in speaker_wavs)
    cached = _latents_cache.get(persona_id)
    if cached and cached[0] == signature:
        _latents_cache.move_to_end(persona_id)
        return cached[1], cached[2]

    get_tts_model()  # ensures _xtts is loaded
    gpt_cond_latent, speaker_embedding = _xtts.get_conditioning_latents(audio_path=speaker_wavs)
    _latents_cache[persona_id] = (signature, gpt_cond_latent, speaker_embedding)
    _latents_cache.move_to_end(persona_id)
    while len(_latents_cache) > MAX_CACHED_VOICES:
        _latents_cache.popitem(last=False)  # evict least-recently-used voice
    return gpt_cond_latent, speaker_embedding


def pcm16_bytes(wav_chunk) -> bytes:
    arr = wav_chunk.detach().cpu().numpy() if hasattr(wav_chunk, "detach") else np.asarray(wav_chunk)
    arr = np.clip(arr, -1.0, 1.0)
    return (arr * 32767.0).astype(np.int16).tobytes()


@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": _tts_model is not None}


@app.post("/synthesize")
async def synthesize(req: SynthesizeRequest):
    speaker_wavs = get_speaker_samples(req.persona_id)
    if not speaker_wavs:
        return JSONResponse(status_code=404, content={"error": "No voice recording saved for this character."})

    try:
        get_tts_model()
        gpt_cond_latent, speaker_embedding = get_conditioning(req.persona_id, speaker_wavs)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Could not load voice model: {e}"})

    try:
        out = _xtts.inference(
            text=req.text,
            language=req.lang,
            gpt_cond_latent=gpt_cond_latent,
            speaker_embedding=speaker_embedding,
        )
        pcm = pcm16_bytes(out["wav"])
        audio_bytes = wav_header(len(pcm)) + pcm
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Speech synthesis failed: {e}"})

    return Response(content=audio_bytes, media_type="audio/wav")


def wav_header(data_len: int, sample_rate: int = OUTPUT_SAMPLE_RATE, channels: int = 1, bits: int = 16) -> bytes:
    """Minimal canonical WAV header for raw PCM16 data, built by hand so
    /synthesize can keep returning a standalone .wav file (as before)
    without a round-trip through a temp file."""
    import struct
    byte_rate = sample_rate * channels * bits // 8
    block_align = channels * bits // 8
    return b"RIFF" + struct.pack("<I", 36 + data_len) + b"WAVEfmt " + struct.pack(
        "<IHHIIHH", 16, 1, channels, sample_rate, byte_rate, block_align, bits
    ) + b"data" + struct.pack("<I", data_len)


@app.post("/synthesize_stream")
async def synthesize_stream(req: SynthesizeRequest):
    speaker_wavs = get_speaker_samples(req.persona_id)
    if not speaker_wavs:
        return JSONResponse(status_code=404, content={"error": "No voice recording saved for this character."})

    try:
        get_tts_model()
        gpt_cond_latent, speaker_embedding = get_conditioning(req.persona_id, speaker_wavs)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Could not load voice model: {e}"})

    def gen():
        try:
            for wav_chunk in _xtts.inference_stream(
                text=req.text,
                language=req.lang,
                gpt_cond_latent=gpt_cond_latent,
                speaker_embedding=speaker_embedding,
                stream_chunk_size=20,
            ):
                yield pcm16_bytes(wav_chunk)
        except Exception as e:
            # Streaming already started (headers sent) — nothing more we can do
            # but stop cleanly; the client's reader just ends short.
            print(f"[tts_server] streaming synthesis error: {e}", file=sys.stderr)

    return StreamingResponse(
        gen(),
        media_type="application/octet-stream",
        headers={"X-Sample-Rate": str(OUTPUT_SAMPLE_RATE), "X-Channels": "1", "X-Format": "s16le"},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
