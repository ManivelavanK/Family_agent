import logging
from fastapi import APIRouter, status
from app.schemas.memory import MemoryLogCreate, CognitiveQuizResponse
from app.schemas.response import APIResponse
from app.ai.groq_service import add_journal_entry, generate_cognitive_quiz

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/memory", tags=["Memory (Cognitive Aid)"])


@router.post("/journal", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def write_journal(log: MemoryLogCreate):
    logger.info("Request received: Save journal entry")
    add_journal_entry(log.entry)
    logger.info("Database updated: Journal entry added to cognitive context")
    return APIResponse(
        success=True,
        message="Journal entry saved to cognitive context.",
        data={"entry": log.entry}
    )


@router.get("/quiz", response_model=APIResponse)
def get_cognitive_quiz():
    logger.info("Request received: Generate cognitive quiz")
    quiz = generate_cognitive_quiz()
    logger.info("Prediction completed: Cognitive quiz generated")
    return APIResponse(
        success=True,
        message="Cognitive quiz generated successfully.",
        data=quiz
    )
