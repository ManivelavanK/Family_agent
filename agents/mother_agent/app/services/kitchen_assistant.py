import logging
from app.ai.llm import call_llm
from app.ai.prompts import KITCHEN_ASSISTANT_PROMPT

logger = logging.getLogger(__name__)


def answer_kitchen_query(query: str) -> str:
    """Answers culinary queries, storage questions, prep tips, and recipe adjustments."""
    logger.info("Answering culinary kitchen query: '%s'", query)
    return call_llm(KITCHEN_ASSISTANT_PROMPT, query)
