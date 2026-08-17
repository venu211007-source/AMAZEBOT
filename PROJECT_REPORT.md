# AmazeBot — Project Report

**An AI-Powered Document, Character-Voice & Molecule Discovery Assistant**

A Project Report submitted in partial fulfilment of the requirements for **B.Tech in Artificial Intelligence and Data Science**, course **Introduction to Material Informatics (23MAT204)**, Amrita Vishwa Vidyapeetham.

**Submitted by:**
- G Venugopalan — CB.AI.U4AID25115
- Selva Vignesh — CB.AI.U4AID25149
- Mahalakshmi R — CB.AI.U4AID25167

**Under the guidance of:** Dr. Suman Dutta
**Head of the Department:** Dr. Soman K P

> A formatted, print-ready version of this report — including the Certificate and Declaration pages with signature blocks — is available as [`AmazeBot_Project_Report.pdf`](AmazeBot_Project_Report.pdf) in this repository.

---

## Certificate

This is to certify that the project report entitled *"AmazeBot: An AI-Powered Document, Character-Voice & Molecule Discovery Assistant"* is a bonafide record of the work carried out by G Venugopalan (CB.AI.U4AID25115), Selva Vignesh (CB.AI.U4AID25149), and Mahalakshmi R (CB.AI.U4AID25167), in partial fulfilment of the requirements for the course Introduction to Material Informatics (23MAT204), B.Tech in Artificial Intelligence and Data Science, Amrita Vishwa Vidyapeetham, during the academic year 2026, under the supervision of the undersigned.

| | |
|---|---|
| **Dr. Suman Dutta** | **Dr. Soman K P** |
| Faculty Guide, Course Faculty — Introduction to Material Informatics | Head of the Department, Department of Artificial Intelligence |

*(Signed copies appear on the PDF version.)*

## Declaration

We hereby declare that the project report entitled *"AmazeBot: An AI-Powered Document, Character-Voice & Molecule Discovery Assistant"*, submitted for the course Introduction to Material Informatics (23MAT204), B.Tech in Artificial Intelligence and Data Science, Amrita Vishwa Vidyapeetham, is a record of original work carried out by us under the guidance of Dr. Suman Dutta, and has not been submitted elsewhere for the award of any degree, diploma, or other similar title.

- G Venugopalan — CB.AI.U4AID25115
- Selva Vignesh — CB.AI.U4AID25149
- Mahalakshmi R — CB.AI.U4AID25167

*(Signed copies appear on the PDF version.)*

---

## Abstract

AmazeBot is an AI-powered assistant that combines three tools in one application: a document Q&A assistant that answers questions grounded in an uploaded paper or report and generates flashcards and quizzes from it; a character-chat feature that lets users talk to custom AI personas using cloned, streamed voice and live hands-free voice calls; and a molecule-discovery tool that turns a plain-language description of a desired material into candidate molecules with interactive 3D structures. The system runs either on the cloud (Gemini API) or fully offline on a local machine with no internet or recurring cost. For molecule discovery, it integrates live with a teammate's independent AI model over a real API, and automatically falls back to locally generated results if that service fails, so the tool stays honest and usable at all times. The project demonstrates a working, integrated implementation of the Conversational-AI and Molecular-Discovery-AI components required by the course.

---

## 1. Introduction

### 1.1 Background

Technical material — research papers, datasheets, lab reports — is time-consuming to read in full when a reader only needs an answer to one specific question. Separately, inverse molecular design (asking a generative model to propose molecules with target properties) is a genuinely useful technique, but it typically exists only as research code, inaccessible to anyone without a specialist's setup. Finally, most student-built AI assistants are text-only, which does not reflect how people naturally think through a problem — by talking it through, interactively, with follow-up.

### 1.2 Why This Problem Is Worth Solving

The course brief requires an integrated system spanning three connected architecture blocks: a **Conversational AI (CAI)** component, a **Molecular-Discovery AI (MD-by-AI)** component, and a **Report Generation** component, working together rather than as isolated demonstrations. AmazeBot is our team's implementation of the CAI block, built to connect live — over a real network API — with a teammate's independently developed MD-by-AI block.

### 1.3 What AmazeBot Is

AmazeBot is a single web application containing three connected tools:

1. **Document Chat** — upload a document, ask grounded questions, generate flashcards and quizzes, and use a Design-AI assistant mode.
2. **Character Chat + Voice** — create custom AI personas with a cloned voice, interact by text or by a live, hands-free voice call.
3. **Molecule Discovery** — describe a target material in plain language and receive candidate molecules with computed formulas and live 3D structures.

It runs in two modes: a **cloud mode** powered by the Google Gemini API, and a **fully offline local mode** powered by a local LLM and local voice models, requiring no API key and no internet connection once set up.

---

## 2. Problem Statement

| # | Problem | Why It Is Hard | Why We Are Solving It |
|---|---|---|---|
| 1 | **Information overload.** Reading a full document to answer one question does not scale. | Answers must stay faithful to the source, across both cloud and fully offline models, without an expensive retrieval pipeline. | Directly reduces study/research time; this is the CAI block required by the course. |
| 2 | **Inaccessible specialist tools.** Inverse molecular design exists only as research code. | Requires integrating live with an independent, still-imperfect external model, and staying honest when it fails. | Without an interface, the underlying MD-by-AI research has no usable front end. |
| 3 | **Shallow interaction.** Text-only assistants do not match natural, spoken interaction. | Real-time voice cloning, streaming synthesis, and hands-free turn-taking are genuine audio-engineering problems, not UI work. | Turns a query tool into something people will actually use conversationally. |

---

## 3. Objectives

- Answer questions from a document using the document's own text, not the model's general knowledge.
- Give the assistant a natural interaction layer: custom personas with cloned, streamed voice and live hands-free voice calls.
- Integrate end-to-end with a teammate's independent MD-by-AI model over a live API — a real cross-project integration, not a stub.
- Support full offline operation, with zero recurring API cost and zero internet dependency once set up.

---

## 4. Literature Review

| Paper | Publisher / Year | Technology Aided | Pros | Gap / Cons |
|---|---|---|---|---|
| Auto-Encoding Variational Bayes (Kingma & Welling) | ICLR, 2014 | Variational Autoencoders (VAE) — generative latent-variable models | Learns a smooth, continuous latent space enabling sampling of new data points | Not chemistry-specific; needs substantial data to learn a meaningful space |
| Automatic Chemical Design Using a Data-Driven Continuous Representation of Molecules (Gómez-Bombarelli et al.) | ACS Central Science, 2018 | Conditional VAE (CVAE) for molecule generation from SMILES | First to demonstrate gradient-based molecule optimization in a learned latent space | Needs tens of thousands of training molecules for reliable generalization — directly relevant, since the teammate's model uses roughly 37 |
| Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks (Lewis et al.) | NeurIPS, 2020 | RAG — grounding LLM answers in external documents via retrieval | Reduces hallucination; scales to large document collections | Adds retrieval/embedding infrastructure and latency — deliberately not used here for single-document Q&A |
| Robust Speech Recognition via Large-Scale Weak Supervision — Whisper (Radford et al.) | OpenAI / arXiv, 2022 | Large-scale weakly-supervised speech-to-text | Strong accuracy across accents and noise without fine-tuning | Full-size models are slow on consumer GPUs — motivated using the lighter faster-whisper variant |
| XTTS: A Massively Multilingual Zero-Shot Text-to-Speech Model (Casanova et al., Coqui) | arXiv, 2024 | Zero-shot voice cloning text-to-speech | Clones a voice from a few seconds of audio, no per-voice training run | Naive full-clip generation has high latency — motivated this project's streaming playback engine |
| Photodynamic Therapy for Cancer (Dolmans, Fukumura & Jain) | Nature Reviews Cancer, 2003 | Domain background — how molecular properties drive PDT drug efficacy | Explains why properties such as energy gap and dipole moment matter for candidate selection | Pre-dates modern generative molecular design — the gap the MD-by-AI block attempts to bridge |

---

## 5. System Architecture

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
             Ollama │   tts_server.py │  MD-by-AI service
          (local LLM)│ (voice cloning, │  (teammate's CVAE
                     │  own process — │   inverse-design
                     │  isolated so a │   model, separate
                     │  native crash  │   repo/process)
                     │  can't take    │
                     │  down chat too)│
```

`main.py` is the single backend origin the browser talks to; it proxies to Ollama, to `tts_server.py`, and to the teammate's MD-by-AI service. Two reasons drive this design: browsers block cross-origin requests by default (CORS), so a single origin avoids that entirely; and isolating voice cloning into its own OS process means a native CUDA/cuDNN crash there cannot take the chat backend down with it.

---

## 6. Implementation

### 6.1 Technology Stack

| Layer | Technology |
|---|---|
| Frontend | Single-file HTML, CSS, vanilla JavaScript — no build step, no framework |
| Frontend libraries (vendored, offline-capable) | marked.js, pdf.js, jszip.js, three.js, chart.js, KaTeX |
| Backend | Python, FastAPI, served via uvicorn |
| Local LLM | Ollama, running `LiquidAI/lfm2.5-1.2b-instruct` |
| Voice cloning / synthesis | XTTS-v2 (Coqui TTS), isolated in `tts_server.py` |
| Speech-to-text | faster-whisper |
| Cheminformatics | RDKit — 3D structure generation, molecular formulas |
| Cloud AI | Google Gemini API |

### 6.2 Local Execution

Four processes run locally, each on its own port:

| Process | Port | Role |
|---|---|---|
| Static file server | 8080 | Serves `AMAZEBOT.html` and its libraries to the browser |
| `main.py` (FastAPI) | 8000 | The single backend origin the browser calls |
| `tts_server.py` | 8001 | Voice cloning, isolated process |
| Ollama | 11434 | Local LLM inference |

### 6.3 Document Understanding — Full Context, Not Retrieval

Document Chat deliberately does not use vector embeddings or a retrieval step. For the document sizes this app targets (single papers or reports, not large corpora), the entire extracted document text is placed directly into the model's context alongside the user's question:

1. **Extract** — text is pulled client-side (PDF.js for PDFs, native multimodal parsing in cloud mode).
2. **Inject** — the full extracted text becomes part of the conversation context.
3. **Generate** — the LLM (Gemini or the local model) answers grounded in that context.

This is a stated trade-off: simpler and more accurate than a full RAG pipeline (chunking, embeddings, cosine-similarity search) for the scale this tool is used at, at the cost of not scaling to very large document collections.

### 6.4 Voice Engine

- **Cloning:** a short reference clip is converted into XTTS-v2 conditioning latents, cached with a bounded LRU (maximum 8 entries) so VRAM cannot be exhausted on a laptop GPU.
- **Streaming playback:** a custom `AudioWorklet`-based ring-buffer player begins speaking as soon as the first audio chunk is generated, with a jitter buffer that absorbs variance in generation speed, instead of waiting for a full clip.
- **Voice Mode:** real-time RMS/energy-based Voice Activity Detection (VAD) drives hands-free turn-taking, allowing the user to interrupt the assistant mid-sentence.

### 6.5 Molecule Discovery Integration

1. The user's plain-language request is parsed by the LLM into structured target parameters (energy gap, dipole moment, hardness, solubility, and others).
2. Parameters are sent over a live HTTP API call to the teammate's MD-by-AI service (a Cloud Run deployment of a Conditional Variational Autoencoder).
3. Returned SMILES strings are rendered as an interactive 3D structure using a hand-built SDF/MOL-block parser and a Three.js renderer.
4. If the live service fails, times out, or returns degraded output, a local RDKit-based fallback generates real candidate structures automatically, explicitly flagged as `is_local_fallback: true`.

### 6.6 APIs Used

| API | Type | Purpose |
|---|---|---|
| Google Gemini API | External REST API | Cloud-mode chat, extraction, and grading |
| AmazeBot's own backend API (`main.py`) | Internal REST API | Frontend ↔ backend communication |
| Ollama's local API | Local REST API | Local-mode chat inference |
| MD-by-AI API | External REST API (teammate's service) | Live molecule-candidate generation |
| Browser Web APIs | Native browser APIs | `MediaRecorder`, `getUserMedia`, `AudioWorklet` for voice capture/playback |

---

## 7. Results

### 7.1 Deliverables Achieved

- Document Chat: Q&A, flashcards, quiz, and Design-AI mode
- Character Chat: custom personas with persistent memory
- Voice cloning (XTTS-v2) with real-time streamed playback
- Voice Mode: live hands-free call with automatic turn-taking
- Molecule Discovery: full-screen mode with saved search history
- Live integration with the teammate's MD-by-AI Cloud Run service
- Resilient local fallback when the live service fails or degrades
- Fully offline local mode (Ollama + on-device voice models)
- Public GitHub repository with a live hosted demo (GitHub Pages)

### 7.2 Progress & Validation

All three tools were implemented and tested end-to-end in both cloud and fully offline modes. Voice reliability issues were root-caused across four separate layers — a sample-rate mismatch, buffer-stitching fragility, an unbounded GPU-memory cache, and GPU contention between the local LLM and the voice model — and fixed one at a time, each verified with real audio-thread capture rather than assumption. Quiz grading was made fair: copy-pasted questions submitted as answers are now detected and scored zero, and genuinely correct answers are no longer under-scored by an overly strict fallback heuristic.

### 7.3 Honest Findings From the Live External Integration

Direct testing of the teammate's live MD-by-AI service uncovered four real limitations in that separate system:

- A small training set (approximately 37 molecules) limits how general the model's learned chemistry is.
- A property-mapping mismatch: the properties AmazeBot requests are not the same properties the model was trained to condition on internally.
- A hardcoded fallback pool of six generic molecules (benzene, phenol, thiophene, pyrimidine, aniline, benzonitrile) is returned whenever generation falls short — the direct cause of an earlier "same molecules every time" symptom.
- The live service was observed returning an empty candidate list even while its own internal statistics reported successful generation.

None of these are fixable from AmazeBot's side, as they originate in a separate repository owned by a teammate. AmazeBot's response was to build a transparent, RDKit-based local fallback that activates automatically and is always clearly labelled, so the feature remains usable and never silently presents an unreliable result as verified.

---

## 8. Challenges & Risks

- **Shared-GPU contention** — the local LLM and the voice model compete for limited VRAM on a single laptop GPU, which caused audio glitches that only appeared under real concurrent load.
- **Streaming audio engineering** — achieving gapless, low-latency playback required several rounds of re-architecture.
- **Dependency on an independently-evolving external service** — Molecule Discovery's result quality is ultimately bounded by a model outside this project's control.
- **Live-demo risk** — if the external service is unstable during a live demonstration, results will visibly and honestly fall back to local candidates rather than fail silently; this is expected behaviour, not a defect.

---

## 9. Next Steps

- Retrain the MD-by-AI model on a larger dataset and correct its property mapping (the teammate's side of the integration).
- Replace the current placeholder fitness score with a real, computed metric once the above is resolved.
- Build the Report Generation block — the one component of the three-part course architecture not yet built by anyone on the team.
- Continue reducing Voice Mode latency for an even more natural live-call experience.

---

## 10. Conclusion

AmazeBot delivers a working implementation of the Conversational-AI block required by the course, integrated end-to-end with a teammate's independent Molecular-Discovery-AI block over a live API. Every feature operates in both cloud and fully offline modes. The project integrated honestly with a real, imperfect, independently-evolving external model — identifying its actual limitations directly from its behaviour rather than assuming it worked, and engineering a transparent fallback rather than concealing failures. What is genuinely this team's own work is the complete application: the frontend, the backend, the voice engine, and the integration layer connecting to the MD-by-AI service. What is not this team's own work is the MD-by-AI model itself.

---

## References

1. D. P. Kingma and M. Welling, "Auto-Encoding Variational Bayes," *ICLR*, 2014.
2. R. Gómez-Bombarelli et al., "Automatic Chemical Design Using a Data-Driven Continuous Representation of Molecules," *ACS Central Science*, 4(2), 2018.
3. P. Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," *NeurIPS*, 2020.
4. A. Radford et al., "Robust Speech Recognition via Large-Scale Weak Supervision," OpenAI / arXiv:2212.04356, 2022.
5. E. Casanova et al., "XTTS: A Massively Multilingual Zero-Shot Text-to-Speech Model," Coqui / arXiv:2406.04904, 2024.
6. M. J. Dolmans, D. Fukumura, and R. K. Jain, "Photodynamic Therapy for Cancer," *Nature Reviews Cancer*, 3, 380–387, 2003.
7. RDKit: Open-Source Cheminformatics Software, rdkit.org.
8. FastAPI, PyTorch, Three.js, PDF.js — open-source libraries used in the AmazeBot implementation.
