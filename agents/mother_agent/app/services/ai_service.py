import logging
import html
from openai import OpenAI, APIError, RateLimitError, APITimeoutError
from app.config import GROQ_API_KEY, GROQ_MODEL

logger = logging.getLogger(__name__)

_client = None

def get_groq_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
        )
    return _client

_FALLBACK = "Unable to generate AI response at this time. Please try again later."


def _sanitize(value: str) -> str:
    """Escape HTML special chars to prevent XSS when output is rendered in browser."""
    return html.escape(str(value))


def call_groq(prompt: str, temperature: float = 0.5, max_tokens: int = 300) -> str:
    try:
        client = get_groq_client()
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except RateLimitError:
        logger.warning("Groq rate limit hit.")
        return "AI service is temporarily rate-limited. Please try again in a moment."
    except APITimeoutError:
        logger.warning("Groq API timeout.")
        return "AI service timed out. Please try again."
    except APIError as e:
        logger.error("Groq API error: %s", e)
        return _FALLBACK
    except Exception as e:
        logger.error("Unexpected error calling Groq: %s", e)
        return _FALLBACK


def generate_recommendation(data: dict) -> str:
    prompt = f"""You are an intelligent grocery assistant.

Analyze this grocery item:
Item Name: {_sanitize(data["item_name"])}
Current Stock: {_sanitize(str(data["current_stock"]))}
Average Daily Usage: {_sanitize(str(data["average_daily_usage"]))}
Estimated Days Remaining: {_sanitize(str(data["estimated_days_remaining"]))}

Provide:
1. When to buy
2. Quantity to buy
3. Storage advice

Keep the recommendation within 4-5 lines. Return only plain text."""
    return call_groq(prompt, temperature=0.5, max_tokens=200)


def generate_recipe_recommendation(prompt: str) -> str:
    return call_groq(prompt, temperature=0.7, max_tokens=600)


def generate_waste_recommendation(prompt: str) -> str:
    return call_groq(prompt, temperature=0.6, max_tokens=400)


def generate_price_recommendation(prompt: str) -> str:
    return call_groq(prompt, temperature=0.5, max_tokens=400)


def generate_planning_recommendation(prompt: str) -> str:
    return call_groq(prompt, temperature=0.5, max_tokens=500)
