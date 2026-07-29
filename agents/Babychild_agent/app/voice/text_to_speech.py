import edge_tts
import logging

logger = logging.getLogger(__name__)

async def synthesize_text(text: str, output_path: str, voice: str = "en-US-AnaNeural") -> str:
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        return output_path
    except Exception as e:
        logger.error(f"Text-to-Speech synthesis failed: {e}")
        raise e
