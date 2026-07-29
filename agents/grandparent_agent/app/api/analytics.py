import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.analytics_service import get_analytics_summary
from app.schemas.response import APIResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@router.get("/", response_model=APIResponse)
def read_analytics_summary(db: Session = Depends(get_db)):
    logger.info("Request received: Read analytics summary")
    summary = get_analytics_summary(db)
    return APIResponse(
        success=True,
        message="Analytics summary compiled successfully",
        data=summary
    )
