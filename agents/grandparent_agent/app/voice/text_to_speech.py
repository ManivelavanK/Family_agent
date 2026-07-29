import logging
import edge_tts

logger = logging.getLogger(__name__)


async def synthesize_speech(text: str, voice: str = "en-US-GuyNeural") -> bytes:
    """
    Synthesizes text into MP3 audio bytes using edge-tts.
    Since this is run inside async FastAPI endpoints, it is natively awaited.
    """
    logger.info("Starting text-to-speech synthesis: '%s'", text)
    try:
        communicate = edge_tts.Communicate(text, voice)
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        
        if not audio_data:
            raise ValueError("No audio data returned from edge-tts stream")
            
        logger.info("Text-to-speech synthesis completed successfully. Bytes: %d", len(audio_data))
        return audio_data
    except Exception as e:
        logger.exception("edge-tts synthesis failed. Using dummy silent MP3 fallback.")
        return get_dummy_silent_mp3()


def get_dummy_silent_mp3() -> bytes:
    """Returns a minimal valid silent MP3 byte sequence."""
    return b'\xff\xfb\x90\x44\x00\x00\x00\x03\x48\x00\x00\x00\x00\x4c\x41\x4d\x45\x33\x2e\x39\x39\x72\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
