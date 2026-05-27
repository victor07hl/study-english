# English Practice Tutor

A modern web application built with Streamlit to practice speaking and listening in English using AI.

## Features
- **URL-Based Practice:** Paste a blog or YouTube link to practice content-specific conversation.
- **Topic-Based Practice:** Practice any topic (e.g., "Job Interview", "Vacation").
- **Real-time Interaction:**
    - **Speaking:** Record your voice directly in the browser.
    - **Listening:** The agent responds with a natural-sounding voice.
- **AI-Powered:**
    - **LLM:** Anthropic Claude (Modular design ready for Gemini).
    - **STT (Speech-to-Text):** Local OpenAI Whisper (Free & Open Source).
    - **TTS (Text-to-Speech):** Microsoft Edge TTS (Free & High Quality).

## Setup Instructions

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Environment Variables:**
   - Create a `.env` file or rename `.env.example`.
   - Add your `ANTHROPIC_API_KEY`.

3. **Run the Application:**
   ```bash
   streamlit run app.py
   ```

## Project Structure
- `app.py`: Main Streamlit UI and app logic.
- `scraper.py`: Content extraction (Web & YouTube).
- `llm_engine.py`: Modular LLM interface (Claude implemented).
- `speech_engine.py`: Free STT and TTS implementation.

## Note on Speech Tools
- The first time you run the app, it will download the Whisper 'base' model (approx. 140MB).
- Audio autoplay is handled via HTML5 injection in Streamlit.
