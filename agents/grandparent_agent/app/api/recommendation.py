import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.recommendation_service import get_personalized_recommendations
from app.schemas.response import APIResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/recommendation", tags=["Recommendation"])


@router.get("/", response_model=APIResponse)
def read_recommendations(db: Session = Depends(get_db)):
    logger.info("Request received: Generate health recommendations")
    recs = get_personalized_recommendations(db)
    return APIResponse(
        success=True,
        message="Recommendations compiled successfully",
        data=recs
    )
