import edge_tts
import whisper
import asyncio
import tempfile
import os
import torch
import soundfile as sf
import io
import ssl

# Fix for macOS SSL certificate issues during model download
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Global variable for the model
_whisper_model = None

def get_whisper_model():
    """
    Lazy loads the Whisper model to avoid crashing on import if there's no internet.
    """
    global _whisper_model
    if _whisper_model is None:
        try:
            # 'base' is a good balance between speed and accuracy
            _whisper_model = whisper.load_model("base")
        except Exception as e:
            print(f"Failed to load Whisper model: {e}")
            raise e
    return _whisper_model

async def text_to_speech_async(text, voice="en-US-GuyNeural"):
    """
    Converts text to speech using edge-tts (free).
    """
    communicate = edge_tts.Communicate(text, voice)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        await communicate.save(tmp_file.name)
        return tmp_file.name

def text_to_speech(text, voice="en-US-GuyNeural"):
    """
    Sync wrapper for edge-tts.
    """
    return asyncio.run(text_to_speech_async(text, voice))

def transcribe_audio(audio_bytes):
    """
    Transcribes audio bytes using local Whisper model.
    """
    try:
        model = get_whisper_model()
    except Exception:
        return "[Error: Could not load Whisper model. Please check your internet connection.]"

    # Save audio bytes to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
        tmp_audio.write(audio_bytes)
        tmp_audio_path = tmp_audio.name

    try:
        # Transcribe
        result = model.transcribe(tmp_audio_path)
        return result["text"].strip()
    except Exception as e:
        print(f"STT Error: {e}")
        return ""
    finally:
        if os.path.exists(tmp_audio_path):
            os.remove(tmp_audio_path)
