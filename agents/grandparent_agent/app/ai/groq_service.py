import json
import logging
from app.ai.llm import call_llm
from app.ai.prompts import COGNITIVE_QUIZ_SYSTEM_PROMPT, RECOMMENDATION_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# Temporary in-memory journal store for simplicity
_journal_entries = []


def add_journal_entry(text: str):
    _journal_entries.append(text)
    if len(_journal_entries) > 10:
        _journal_entries.pop(0)


def generate_cognitive_quiz() -> dict:
    context = "\n".join(_journal_entries) if _journal_entries else "General knowledge and cognitive memory check."
    user_prompt = f"Journal context or background information:\n{context}\n\nGenerate the memory challenge."
    try:
        response_text = call_llm(
            system_prompt=COGNITIVE_QUIZ_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            json_response=True
        )
        return json.loads(response_text)
    except Exception as e:
        logger.error(f"Error decoding cognitive quiz JSON: {e}")
        return {}


def generate_health_recommendations(summary_data: dict) -> dict:
    user_prompt = f"Analyze health data log:\n{json.dumps(summary_data, indent=2)}\n\nProvide recommendations."
    try:
        response_text = call_llm(
            system_prompt=RECOMMENDATION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            json_response=True
        )
        return json.loads(response_text)
    except Exception as e:
        logger.error(f"Error decoding recommendations JSON: {e}")
        return {}
