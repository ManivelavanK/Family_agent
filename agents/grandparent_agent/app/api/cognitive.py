import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.response import APIResponse
from app.schemas.cognitive import CognitiveJournalCreate, CognitiveJournalResponse, CognitiveReportResponse
from app.services.cognitive_service import (
    save_cognitive_journal,
    generate_personalized_cognitive_quiz,
    get_cognitive_report_summary
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/cognitive", tags=["Cognitive Care"])


@router.post("/journal", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def write_cognitive_journal(journal_in: CognitiveJournalCreate, db: Session = Depends(get_db)):
    """
    Records daily reflection logs, registers mood parameter, and calculates daily Memory Score.
    """
    logger.info("Request received: Save daily mood journal")
    log = save_cognitive_journal(db, journal_in)
    return APIResponse(
        success=True,
        message="Journal entry and mood saved successfully",
        data=CognitiveJournalResponse.model_validate(log).model_dump()
    )


@router.get("/quiz", response_model=APIResponse)
def read_cognitive_quiz(db: Session = Depends(get_db)):
    """
    Generates customized multiple choice memory quiz questions based on the grandparent's past reflections.
    """
    logger.info("Request received: Get cognitive memory quiz")
    quiz = generate_personalized_cognitive_quiz(db)
    return APIResponse(
        success=True,
        message="Cognitive quiz generated successfully",
        data=quiz
    )


@router.get("/report", response_model=APIResponse)
def read_cognitive_report(db: Session = Depends(get_db)):
    """
    Retrieves report cards compiling Weekly Cognitive Score, mood trends, and recommended brain exercises.
    """
    logger.info("Request received: Get cognitive report card")
    report = get_cognitive_report_summary(db)
    return APIResponse(
        success=True,
        message="Weekly cognitive report compiled successfully",
        data=report
    )
