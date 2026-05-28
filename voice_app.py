"""English Practice Tutor — voice mode.

FastAPI backend that serves a single-page voice UI. The browser handles
speech-to-text (Web Speech API) and text-to-speech (SpeechSynthesis) natively;
this server only orchestrates the conversation with Claude.

Run with:
    uvicorn voice_app:app --reload --port 8000
"""

from __future__ import annotations

import os
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from scraper import get_content_from_link

load_dotenv()

BASE = Path(__file__).parent
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-opus-4-7")

app = FastAPI(title="English Practice Tutor — Voice")
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")

_client: Anthropic | None = None


def client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic()
    return _client


# ── System prompts ───────────────────────────────────────────────────────────

# Voice-optimised: no Markdown, no bullet points — everything is spoken aloud.
TUTOR_VOICE_SYSTEM = """You are a warm, encouraging English tutor having a spoken conversation with a learner.
Everything you say will be read aloud by a text-to-speech engine, so:
- Use plain spoken language only. No Markdown, no bullet points, no asterisks, no dashes, no code blocks.
- Keep every response to two or three short sentences — one brief reaction and one question.
- Always end with exactly one clear question to keep the learner talking.
- If the learner makes a grammatical mistake, gently correct it in a natural way before asking your next question.
- Speak like a friendly human. Use contractions. Be warm and direct.
- Do not start with generic greetings like "Hello!" or "Great!". Jump straight into the topic.

Topic context:
{content}
"""

FEEDBACK_SYSTEM = """You are a warm English tutor giving spoken feedback at the end of a practice session.
Everything you say will be read aloud, so use plain conversational language only — no Markdown, no bullet points, no special characters.
Review the conversation and give the learner:
1. A score out of 10 for their English (mention it naturally, like "I'd give you a 7 out of 10").
2. Two or three things they did well.
3. One or two specific areas to improve, with a concrete tip.
4. One phrase or sentence they said that you'd suggest rephrasing, and how.
Keep it friendly, encouraging, and under a minute of speech. Speak directly to the learner.
"""

FEEDBACK_USER_MSG = (
    "The practice session is over. Please give me my spoken feedback now — "
    "score, what I did well, what to improve, and one example sentence to rephrase."
)


# ── Schemas ─────────────────────────────────────────────────────────────────

class StartReq(BaseModel):
    source_type: str   # "predefined" | "custom" | "url"
    value: str


class ChatReq(BaseModel):
    messages: list[dict]
    content: str


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
def home():
    return FileResponse(BASE / "static" / "index.html")


@app.get("/api/topics")
def get_topics():
    topics_dir = BASE / "topics"
    topic_files = sorted([f for f in os.listdir(topics_dir) if f.endswith(".md")])
    return [
        {"id": f, "name": f.replace(".md", "").replace("_", " ").title()}
        for f in topic_files
    ]


@app.post("/api/start")
async def start_session(req: StartReq):
    content = ""
    if req.source_type == "predefined":
        path = BASE / "topics" / req.value
        if not path.exists():
            raise HTTPException(status_code=404, detail=f"Topic file not found: {req.value}")
        content = path.read_text(encoding="utf-8")
    elif req.source_type == "custom":
        content = f"The learner wants to practise English by talking about: {req.value}"
    elif req.source_type == "url":
        content = get_content_from_link(req.value)
        if not content:
            raise HTTPException(status_code=400, detail="Could not extract content from that URL")
    else:
        raise HTTPException(status_code=400, detail=f"Unknown source_type: {req.source_type!r}")

    system = TUTOR_VOICE_SYSTEM.format(content=content[:3000])
    initial_msgs = [{"role": "user", "content": "I'm ready to practise. Please introduce the topic and ask your first question."}]

    resp = client().messages.create(
        model=MODEL,
        max_tokens=300,
        system=system,
        messages=initial_msgs,
    )
    reply = "".join(block.text for block in resp.content if block.type == "text")

    return {"content": content, "initial_reply": reply}


@app.post("/api/chat")
async def chat(req: ChatReq):
    if not req.content:
        raise HTTPException(status_code=400, detail="No session content provided")

    system = TUTOR_VOICE_SYSTEM.format(content=req.content[:3000])

    resp = client().messages.create(
        model=MODEL,
        max_tokens=300,
        system=system,
        messages=req.messages,
    )
    reply = "".join(block.text for block in resp.content if block.type == "text")
    return {"reply": reply}


@app.post("/api/feedback")
async def feedback(req: ChatReq):
    """Return a spoken end-of-session evaluation — no Markdown, TTS-friendly."""
    if not req.messages:
        raise HTTPException(status_code=400, detail="No conversation to evaluate")

    msgs = list(req.messages) + [{"role": "user", "content": FEEDBACK_USER_MSG}]

    resp = client().messages.create(
        model=MODEL,
        max_tokens=600,
        system=FEEDBACK_SYSTEM,
        messages=msgs,
    )
    reply = "".join(block.text for block in resp.content if block.type == "text")
    return {"reply": reply}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
