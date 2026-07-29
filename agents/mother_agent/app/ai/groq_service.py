import logging
from app.ai.llm import call_llm

logger = logging.getLogger(__name__)


def generate_reflection_summary(item_name: str, memory_summary: str) -> str:
    prompt = f"""Based on these consumption memory records for '{item_name}':
{memory_summary}

Generate:
1. A one-sentence insight about consumption pattern
2. A one-sentence recommendation for the family

Return only plain text, 2 lines."""
    return call_llm("You are a family grocery analyst.", prompt)
