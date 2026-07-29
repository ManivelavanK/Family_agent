from sqlalchemy.orm import Session
import os
import uuid
import asyncio
import logging

from app.voice import speech_to_text, text_to_speech
from app.services import ai_service

logger = logging.getLogger(__name__)

# Configure a temporary audio directory inside the workspace
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMP_DIR = os.path.join(BASE_DIR, "temp_audio")
os.makedirs(TEMP_DIR, exist_ok=True)

async def process_voice_query(db: Session, baby_id: int, audio_bytes: bytes, filename: str) -> dict:
    # 1. Generate unique file names
    unique_id = uuid.uuid4().hex
    _, ext = os.path.splitext(filename)
    if not ext:
        ext = ".wav"  # fallback
    
    input_file_path = os.path.join(TEMP_DIR, f"input_{unique_id}{ext}")
    output_file_path = os.path.join(TEMP_DIR, f"output_{unique_id}.mp3")

    try:
        # Save upload file bytes to disk
        with open(input_file_path, "wb") as f:
            f.write(audio_bytes)
            
        # 2. Whisper Speech-to-Text
        recognized_text = speech_to_text.transcribe_audio(input_file_path)
        logger.info(f"Voice query transcribed: '{recognized_text}'")
        
        if not recognized_text or not recognized_text.strip():
            recognized_text = "Hello"  # default fallback if silent

        # 3. AI Insights Answer
        ai_answer = ai_service.get_ai_insights(db=db, baby_id=baby_id, question=recognized_text)
        logger.info(f"AI Response generated: '{ai_answer}'")

        # 4. Text-to-Speech
        await text_to_speech.synthesize_text(text=ai_answer, output_path=output_file_path)
        logger.info(f"Response synthesized to audio at: {output_file_path}")

        return {
            "recognized_text": recognized_text,
            "ai_answer": ai_answer,
            "audio_file_path": output_file_path
        }
    except Exception as e:
        logger.error(f"Error processing voice query: {e}")
        # Clean up output path if it was created
        if os.path.exists(output_file_path):
            try:
                os.remove(output_file_path)
            except Exception:
                pass
        raise e
    finally:
        # Clean up temporary input file
        if os.path.exists(input_file_path):
            try:
                os.remove(input_file_path)
            except Exception as cleanup_err:
                logger.warning(f"Failed to clean up temporary input audio file: {cleanup_err}")
