# AmazeBot — AI-Powered Document, Character & Molecule Discovery Assistant

A semester project built for the course *Introduction to Material Informatics* at Amrita Vishwa Vidyapeetham.

AmazeBot started as a document assistant — upload a paper or report and ask questions about it instead of reading the whole thing. It has since grown into three connected tools in one app:

1. **Document Chat** — upload a document, ask questions, generate flashcards/quizzes/design notes from it
2. **Character Chat** — create custom AI personas with their own personality and a cloned voice, and talk to them by text or live voice call
3. **Molecule Discovery** — describe a material you want (target energy gap, solubility, toxicity, etc.) and get candidate molecules back from a teammate's generative model, in a dedicated full-screen research view

Everything runs either against Google's Gemini API (cloud mode, needs an API key) or **fully offline** on your own machine via a local LLM + local voice models (no API key, no internet required once set up).

## Features

### Document Chat
- **Document Q&A** — upload a document and ask questions; answers are grounded in the document's own text
- **Flashcard Generation** — auto-generates flashcards from the document for revision
- **Quiz Generation** — auto-generates quizzes to test understanding of the document
- **Design AI** — a design-engineering assistant mode for working through design problems referencing the uploaded document

### Character Chat & Voice
- **Custom personas** — define a character's name, personality, and speech style/tone
- **Voice cloning** — upload one or more short voice clips and the character replies in that cloned voice (via XTTS‑v2), with fast streamed playback instead of waiting for the whole clip to generate
- **Voice Mode** — a live, hands-free, ChatGPT-style voice call with a character: it listens, auto-detects when you stop talking, replies out loud in the character's own voice, and lets you interrupt it mid-sentence
- **Indian-accent voice preset** — upload one reference clip once and it becomes a selectable narrator voice for any character that doesn't have its own recording

### Molecule Discovery
- Describe the material properties you want in plain language (energy gap, water solubility, toxicity, dipole moment, hardness, etc.)
- AmazeBot extracts structured target parameters and sends them to **MD‑by‑AI**, a teammate's separate inverse molecular-design service (a CVAE-based generative model), and shows back candidate molecules (SMILES, 3D structure, computed formula)
- Has its own dedicated full-screen view (not a popup) with a saved search history, so past results can be revisited instantly without re-running generation
- **Honest about its own limits** — the results panel plainly explains and visibly flags the underlying model's known limitations (see *Known Limitations* below) instead of presenting every result as a verified prediction

### Two ways to run it
- **Cloud mode** — powered by the Gemini API; needs a free API key from [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
- **Local mode** — powered by a local LLM (Ollama, `LiquidAI/lfm2.5-1.2b-instruct`) plus local voice models (XTTS‑v2 for cloning, faster-whisper for speech-to-text); no API key, no internet needed once models are downloaded. Local mode covers Document Chat, Flashcards, Quiz, Design AI, and Character Chat/Voice Mode.

## How Document Chat Works

Document Chat does **not** use vector embeddings or a retrieval step — for the document sizes this app targets (single papers/reports, not large corpora), the whole extracted document text is kept as context and sent directly to the LLM alongside the user's question:

1. **Extract** — the uploaded document's text is extracted client-side (PDF.js for PDFs; Gemini's native multimodal parsing when in cloud mode)
2. **Inject** — the extracted text becomes part of the conversation context sent to the LLM
3. **Generate** — the LLM (Gemini or the local model) answers grounded in that context

This is simpler than a full RAG (retrieval-augmented generation) pipeline with chunking/embeddings/cosine-similarity search, and is a deliberate trade-off: for the size of documents this app is actually used with, "just give the model the whole document" is more accurate and much simpler than retrieval, at the cost of not scaling to very large document collections.

## Architecture — how the three tools connect

Following the course project architecture (CAI ↔ MD-by-AI ↔ Report Gen):

```
                 ┌─────────────────────────────┐
   Browser  ───▶ │        AmazeBot ("CAI")      │
  (AMAZEBOT.html)│  single-page app, no build   │
                 └───────────────┬─────────────┘
                                 │  HTTP (localhost)
                 ┌───────────────▼─────────────┐
                 │   Local backend (main.py)    │
                 │   FastAPI — one origin for    │
                 │   the browser to talk to      │
                 └──┬───────────┬───────────┬───┘
                    │           │           │
             Ollama │    tts_server.py│  MD-by-AI service
          (local LLM)│ (voice cloning,│  (teammate's CVAE
                     │  own process — │   inverse-design
                     │  isolated so a │   model, separate
                     │  native crash  │   repo/process)
                     │  can't take    │
                     │  down chat too)│
```

- `main.py` is the single backend origin the browser talks to. It proxies requests to Ollama (chat), a separate `tts_server.py` process (voice cloning/synthesis), and the teammate's MD‑by‑AI service — mainly to dodge browser CORS restrictions and so a crash in one component (voice cloning has occasionally crashed the whole process outright on native CUDA/cuDNN errors) can't take down the others.
- `tts_server.py` runs XTTS‑v2 for voice cloning and streams synthesized audio back in real time via a ring-buffer `AudioWorklet` player in the browser, instead of waiting for a full clip to generate before playing anything.
- MD‑by‑AI is not part of this repo — it's a teammate's separate project, expected to be running locally on port 8002.

## Known Limitations (Molecule Discovery)

Confirmed by reading the current MD‑by‑AI source directly — these are limitations of that separate model, not of AmazeBot's integration:

- **Small training set** — the underlying CVAE is trained on 37 hand-picked molecules, not nearly enough to learn general chemistry.
- **Property mismatch** — the 9 properties AmazeBot asks for (energy gap, dipole moment, hardness, etc.) aren't the same 9 properties the model was actually trained to condition on internally, so generation isn't well steered by the specific request yet.
- **Fallback padding** — when the model can't generate enough valid, unique molecules on its own, results get padded with a fixed pool of generic building blocks (benzene, phenol, thiophene, pyrimidine, aniline, benzonitrile). AmazeBot detects and flags these in the UI so they aren't mistaken for optimized results.
- The "fitness" score shown per candidate is currently a placeholder, not a computed metric.

None of this is fixable from AmazeBot's side — fixing it means retraining the CVAE on a larger dataset and fixing the property-mapping bug in the MD‑by‑AI repo itself.

## Running It

### Cloud mode (quickest)
1. Open `AMAZEBOT.html` (via a local static server, e.g. `python -m http.server 8080`, then visit `http://localhost:8080/AMAZEBOT.html` — opening the file directly can break some browser APIs)
2. Enter a Gemini API key when prompted ([get one free](https://aistudio.google.com/apikey))

### Local mode (fully offline)
1. Install and start [Ollama](https://ollama.com), then pull the model:
   ```
   ollama pull LiquidAI/lfm2.5-1.2b-instruct
   ollama serve
   ```
2. Set up and start the backend:
   ```
   cd backend
   start_backend.bat
   ```
   This creates a venv, installs `requirements.txt`, and starts `main.py` on port 8000 (which in turn spawns `tts_server.py` on port 8001 for voice cloning). Voice cloning additionally needs `torch` (CUDA build recommended) and `TTS` (Coqui TTS) installed in the same venv — these aren't in `requirements.txt` because the correct `torch` install is CUDA-version-specific; see [pytorch.org](https://pytorch.org/get-started/locally/) for the right command for your GPU.
3. Serve and open `AMAZEBOT.html` as above, then toggle Local Mode / open Character Chat.
4. For Molecule Discovery, the teammate's MD‑by‑AI service needs to be running separately on port 8002.

## Technology

- **Frontend**: single-file HTML/CSS/JavaScript, no build step — `marked.js` for markdown rendering, `Chart.js`/`Three.js` for visualization, `pdf.js` for client-side PDF parsing, the native `Web Audio API`/`AudioWorklet` for streamed voice playback, `MediaRecorder`/`getUserMedia` for Voice Mode's microphone input
- **Cloud AI**: Google Gemini API
- **Local AI**: Ollama (`LiquidAI/lfm2.5-1.2b-instruct`) for chat, XTTS‑v2 (Coqui TTS) for voice cloning, faster-whisper for speech-to-text
- **Backend**: FastAPI (Python) — `main.py` (chat/transcription/proxying) + `tts_server.py` (voice cloning, isolated into its own process)
- **Molecule Discovery**: RDKit for molecule handling/3D structure generation, a CVAE (Conditional Variational Autoencoder) for inverse molecular design (teammate's separate MD‑by‑AI repo)

## Team

- G Venugopalan — CB.AI.U4AID25115
- Selva Vignesh — CB.AI.U4AID25149
- Mahalakshmi R — CB.AI.U4AID25167

## Course

Introduction to Material Informatics — Amrita Vishwa Vidyapeetham
