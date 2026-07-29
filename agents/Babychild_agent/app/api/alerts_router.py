from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging
from typing import Optional

from app.database.database import get_db
from app.services import rule_service, baby_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/alerts", tags=["Alerts Engine"])

@router.get("/{baby_id}")
def get_baby_alerts(baby_id: int, family_id: Optional[int] = None, db: Session = Depends(get_db)):
    try:
        # Validate baby exists
        baby = baby_service.get_baby_by_id(db=db, baby_id=baby_id)
        if not baby:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Baby with ID {baby_id} not found."
            )
            
        # Validate family ownership
        if family_id is not None and baby.family_id != family_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Baby profile does not belong to this family."
            )
            
        alerts_data = rule_service.generate_alerts(db=db, baby_id=baby_id)
        return {
            "success": True,
            "message": "Baby alerts evaluated successfully.",
            "data": alerts_data
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating alerts for baby {baby_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating baby alerts."
        )
