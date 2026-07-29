from groq import Groq
from app.config import GROQ_API_KEY, GROQ_MODEL
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def call_groq(prompt: str, system_prompt: Optional[str] = None) -> str:
    if not GROQ_API_KEY or GROQ_API_KEY == "gsk_placeholder":
        raise ValueError("GROQ_API_KEY is not configured or has placeholder values.")
        
    try:
        client = Groq(api_key=GROQ_API_KEY)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        chat_completion = client.chat.completions.create(
            messages=messages,
            model=GROQ_MODEL,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        logger.error(f"Failed to communicate with Groq API: {e}")
        raise e
