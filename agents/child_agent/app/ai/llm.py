import os
import json
import logging
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def get_groq_client() -> Groq | None:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.warning("GROQ_API_KEY not found in environment.")
        return None
    try:
        return Groq(api_key=api_key)
    except Exception as e:
        logger.error(f"Failed to initialize Groq client: {e}")
        return None

def query_llm(system_prompt: str, user_prompt: str, response_json: bool = False, temperature: float = 0.5) -> str:
    """Queries the Groq API with the system and user prompts."""
    client = get_groq_client()
    if not client:
        return "Error: Groq API key is not configured."
    
    try:
        kwargs = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature
        }
        if response_json:
            kwargs["response_format"] = {"type": "json_object"}
            
        response = client.chat.completions.create(**kwargs)
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error querying Groq: {e}")
        return json.dumps({
            "error": f"LLM Query failed: {str(e)}",
            "answer": "I'm having trouble connecting to the AI brain right now. Please try again."
        })
