from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.profile import ChildProfile
from app.schemas.ai_intelligence import ChildAIIntelligenceReport
from app.services.ai.child_intelligence_service import ChildIntelligenceService

router = APIRouter(tags=["Child AI Intelligence Agent"])


@router.get(
    "/children/intelligence/{child_id}",
    response_model=ChildAIIntelligenceReport,
    status_code=status.HTTP_200_OK,
)
def get_child_ai_intelligence(
    child_id: int,
    db: Session = Depends(get_db),
):
    """
    Step 8: GET /children/intelligence/{child_id}
    Returns current AI-generated child intelligence briefing including academic, wellbeing, routine,
    financial, and safety status along with recommended actions and parent notification decision.
    """
    child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child profile with ID {child_id} not found.",
        )

    service = ChildIntelligenceService(db=db)
    return service.analyze_child_intelligence(child_id=child_id, trigger_parent_whatsapp=False)


@router.post(
    "/children/intelligence/{child_id}/analyze",
    response_model=ChildAIIntelligenceReport,
    status_code=status.HTTP_200_OK,
)
def trigger_child_ai_intelligence_analysis(
    child_id: int,
    trigger_whatsapp: bool = Query(False, description="Whether to trigger parent WhatsApp dispatch if notification decision is active"),
    db: Session = Depends(get_db),
):
    """
    Step 8: POST /children/intelligence/{child_id}/analyze
    Manually triggers fresh AI child intelligence analysis and optionally dispatches parent WhatsApp message.
    """
    child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child profile with ID {child_id} not found.",
        )

    service = ChildIntelligenceService(db=db)
    return service.analyze_child_intelligence(child_id=child_id, trigger_parent_whatsapp=trigger_whatsapp)
