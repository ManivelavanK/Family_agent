from groq import Groq
from app.config import GROQ_API_KEY
import os
import logging

logger = logging.getLogger(__name__)

def transcribe_audio(file_path: str) -> str:
    if not GROQ_API_KEY or GROQ_API_KEY == "gsk_placeholder":
        raise ValueError("GROQ_API_KEY is not configured.")
        
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file {file_path} not found.")
        
    try:
        client = Groq(api_key=GROQ_API_KEY)
        with open(file_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=file,
                model="whisper-large-v3"
            )
            return getattr(transcription, "text", "")
    except Exception as e:
        logger.error(f"Speech-to-Text transcription failed: {e}")
        raise e
