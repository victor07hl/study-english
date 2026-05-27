# English Practice Tutor - Project Context

This file contains foundational instructions and architectural context for the English Practice Web App.

## Project Overview
A Streamlit-based application designed for English learners to practice speaking and listening. It uses LLMs to generate content-based or topic-based practice sessions and utilizes free tools for audio interaction.

## Core Mandates & Architecture
- **Framework:** Streamlit for the frontend.
- **Modular LLM Design:** 
  - The `llm_engine.py` is designed to be provider-agnostic.
  - Initial implementation uses **Anthropic Claude**.
  - Future requirement: Implement **Google Gemini** as a standard provider.
- **Free Speech Stack:** 
  - **TTS:** `edge-tts` (Microsoft Edge) for cost-free, high-quality audio.
  - **STT:** Local `openai-whisper` (base model) for private, free transcription.
- **Content Sources:**
  - Blogs/Articles: Handled by `trafilatura`.
  - YouTube: Handled by `youtube-transcript-api`.

## Technical Conventions
- **State Management:** Use `st.session_state` to maintain chat history, extracted content, and audio paths.
- **Audio Handling:** Use base64-encoded HTML5 `<audio>` tags for automatic playback of agent responses.
- **Error Handling:** Always provide user-friendly error messages in the UI if scraping or API calls fail.
- **Persona:** The "Tutor" should be encouraging, concise, and provide gentle grammatical corrections.

## File Structure
- `app.py`: UI and orchestration.
- `llm_engine.py`: LLM provider logic and system prompts.
- `speech_engine.py`: Audio processing (STT/TTS).
- `scraper.py`: Content extraction logic.
- `requirements.txt`: Project dependencies.
- `.env`: API keys and environment configuration.
