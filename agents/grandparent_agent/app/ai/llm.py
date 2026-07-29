import logging
import json
from groq import Groq
from app.config import GROQ_API_KEY, GROQ_MODEL

logger = logging.getLogger(__name__)


def get_llm_client():
    if not GROQ_API_KEY or "replace_with" in GROQ_API_KEY or GROQ_API_KEY == "mock_key_replace_with_actual":
        return None
    try:
        return Groq(api_key=GROQ_API_KEY)
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
    if "quiz" in system_prompt.lower() or "quiz" in user_prompt.lower():
        # cognitive memory helper response
        mock_quiz = {
            "quiz_title": "Daily Memory Challenge",
            "questions": [
                {
                    "question": "What is the capital of France?",
                    "options": ["Paris", "London", "Berlin", "Madrid"],
                    "correct_answer": "Paris"
                },
                {
                    "question": "Which season comes after Summer?",
                    "options": ["Spring", "Autumn", "Winter", "Summer"],
                    "correct_answer": "Autumn"
                }
            ]
        }
        return json.dumps(mock_quiz)

    if "recommendation" in system_prompt.lower() or "recommendation" in user_prompt.lower():
        mock_recs = {
            "summary": "Based on your recent vitals and activity logs, your wellness plan is tracking well.",
            "recommendations": [
                {
                    "category": "Diet",
                    "suggestion": "Increase hydration by consuming 500ml more water before 6:00 PM.",
                    "rationale": "Slightly low water intake logged yesterday."
                },
                {
                    "category": "Fitness",
                    "suggestion": "Engage in a 15-minute light walking session.",
                    "rationale": "Steps are 2,000 below your average target."
                },
                {
                    "category": "Cognitive",
                    "suggestion": "Complete today's memory journal challenge.",
                    "rationale": "Keeps mental sharpness optimized."
                }
            ]
        }
        return json.dumps(mock_recs)

    return "Mock Response: AI capabilities are active (configure GROQ_API_KEY for actual API calls)."
