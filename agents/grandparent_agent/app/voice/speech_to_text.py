import logging
from app.ai.llm import get_llm_client

logger = logging.getLogger(__name__)


def transcribe_audio(file_bytes: bytes, filename: str) -> str:
    """
    Transcribes audio bytes using Groq's OpenAI-compatible Whisper model.
    Falls back to a rule-based mock transcription if the Groq client is not initialized.
    """
    logger.info("Starting audio transcription for file: %s", filename)
    client = get_llm_client()

    if not client:
        logger.warning("Groq client not available. Using mock transcription fallback.")
        return get_mock_transcription(filename)

    try:
        # Groq client expects a tuple of (filename, file_bytes) or a file-like object
        response = client.audio.transcriptions.create(
            file=(filename, file_bytes),
            model="whisper-large-v3",
            response_format="json"
        )
        transcription_text = response.text
        logger.info("Groq transcription success: '%s'", transcription_text)
        return transcription_text
    except Exception as e:
        logger.exception("Groq transcription API failed. Falling back to mock transcription.")
        return get_mock_transcription(filename)


def get_mock_transcription(filename: str) -> str:
    """Returns static test transcription values depending on the filename keywords."""
    name_lower = filename.lower()
    if "med" in name_lower or "pill" in name_lower:
        return "Did I take my medicine today?"
    if "app" in name_lower or "doc" in name_lower:
        return "When is my next appointment?"
    if "help" in name_lower or "sos" in name_lower:
        return "I need help"
    if "sugar" in name_lower or "bp" in name_lower or "vital" in name_lower:
        return "What is my blood pressure?"
    if "eat" in name_lower or "food" in name_lower or "recommend" in name_lower:
        return "What should I eat today?"
    if "journal" in name_lower or "diary" in name_lower:
        return "Record today's journal"
    return "Did I take my medicine today?"
