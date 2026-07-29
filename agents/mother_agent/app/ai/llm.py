import logging
import json
from openai import OpenAI
from app.config import GROQ_API_KEY, GROQ_MODEL

logger = logging.getLogger(__name__)


def get_llm_client():
    if not GROQ_API_KEY or "replace_with" in GROQ_API_KEY or GROQ_API_KEY == "mock_key_replace_with_actual":
        return None
    try:
        # Use OpenAI client pointing to Groq's endpoint (standard style)
        return OpenAI(
            api_key=GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
        )
    except Exception as e:
        logger.error(f"Failed to create Groq client: {e}")
        return None


def call_llm(system_prompt: str, user_prompt: str, json_response: bool = False) -> str:
    client = get_llm_client()
    if not client:
        logger.warning("Groq API client is not initialized. Using Mock LLM Response.")
        return get_mock_response(system_prompt, user_prompt)

    try:
        response_format = {"type": "json_object"} if json_response else None
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            model=GROQ_MODEL,
            response_format=response_format,
            temperature=0.7,
        )
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"Error calling LLM API: {e}")
        return get_mock_response(system_prompt, user_prompt)


def get_mock_response(system_prompt: str, user_prompt: str) -> str:
    """Generates synthetic responses mimicking LLM output for testing purposes."""
    text = user_prompt.lower()
    if "recipe" in text:
        return (
            "Based on your stock, you can make Quick Garlic Butter Noodles. "
            "Boil noodles, toss in melted butter, minced garlic, and dynamic soy sauce. "
            "Garnish with green onions."
        )
    if "storage" in text or "store" in text:
        return "Keep tomatoes at room temperature away from direct sunlight. Once fully ripe, store in the fridge."
    if "substitute" in text or "substitution" in text:
        return "You can substitute buttermilk with milk mixed with 1 tablespoon of lemon juice or white vinegar."
    
    return "Mock Response: Kitchen intelligence features are active (configure GROQ_API_KEY for actual API calls)."
