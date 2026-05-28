# CLAUDE.md

This file provides context for Claude Code when working in this repository.

## What this project is

**English Practice Tutor** — a conversational AI app that helps users practise spoken English.
The user picks a topic (pre-defined, custom, or from a URL/YouTube video), and the AI tutor
asks questions, gives gentle grammar corrections, and keeps the conversation going.

There are **two separate apps** that share the same backend logic:

| App | File | How to run |
|-----|------|-----------|
| Streamlit (audio recorder + autoplay) | `app.py` | `streamlit run app.py` |
| FastAPI + browser voice UI (Web Speech API) | `voice_app.py` | `uvicorn voice_app:app --reload --port 8000` |

## Python environment

```
source /Users/victormoreno/python_envs/english_env/bin/activate
```

## Project layout

```
study-english/
├── app.py               # Streamlit app — uses st.audio_input + whisper + edge-tts
├── voice_app.py         # FastAPI backend for the voice SPA
├── llm_engine.py        # Claude provider + Streamlit-oriented system prompt
├── speech_engine.py     # edge-tts (TTS) + openai-whisper (STT) — used by app.py only
├── scraper.py           # Extracts text from blog URLs and YouTube transcripts
├── static/
│   └── index.html       # Single-page voice UI (served by voice_app.py)
├── topics/              # Pre-defined topic markdown files
│   ├── technology.md
│   ├── travel.md
│   ├── daily_routine.md
│   └── job_interview.md
├── requirements.txt
└── .env                 # ANTHROPIC_API_KEY (and optionally ANTHROPIC_MODEL)
```

## Environment variables (`.env`)

```
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-opus-4-7   # optional — defaults to claude-opus-4-7
```

## Key design decisions

### Two apps, one codebase
- **`app.py`** (Streamlit): uses `st.audio_input()` for recording, local Whisper for STT, and
  `edge-tts` for TTS. Heavy dependencies but works fully server-side.
- **`voice_app.py`** (FastAPI): delegates all audio to the browser via the Web Speech API
  (`SpeechRecognition` for STT, `SpeechSynthesis` for TTS). Much lighter — no audio deps needed.

### Voice-optimised system prompts
`voice_app.py` uses `TUTOR_VOICE_SYSTEM` — a prompt that explicitly forbids Markdown, bullet
points, and special characters because the response is read aloud by the browser's TTS engine.
`app.py` uses the `TUTOR_SYSTEM_PROMPT` from `llm_engine.py` which allows richer formatting.

### Content sources
Both apps support three sources:
1. **Pre-defined topics** — markdown files in `topics/`
2. **Custom topic** — freeform text input
3. **URL** — `scraper.py` extracts text from blog articles or YouTube transcripts

### Feedback / wrap-up
The voice app has a **"Get session feedback"** button that calls `/api/feedback`.
This uses a separate `FEEDBACK_SYSTEM` prompt to produce a spoken, TTS-friendly evaluation:
score out of 10, strengths, areas to improve, and one example sentence to rephrase.

## Adding a new topic

Create a markdown file in `topics/` — e.g. `sports.md`. It will automatically appear in both apps.

## API routes (voice_app.py)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Serve `static/index.html` |
| GET | `/api/topics` | List available topic files |
| POST | `/api/start` | Start a session — returns `{content, initial_reply}` |
| POST | `/api/chat` | Continue conversation — returns `{reply}` |
| POST | `/api/feedback` | End-of-session spoken evaluation — returns `{reply}` |

## UI features (static/index.html)

- 🎤 Mic button with three visual states: idle / recording (pulse animation) / TTS speaking (amber)
- Typing indicator (animated dots) while waiting for Claude
- TTS speaking indicator in the header with animated dots
- Interim transcript preview while the user speaks
- Recording timer
- **Send** button to explicitly submit an answer
- **⟳ Replay** button to replay the last tutor message
- **Stop speaking** button to interrupt TTS
- **Space bar** shortcut to toggle recording
- Voice picker to choose the browser TTS voice
