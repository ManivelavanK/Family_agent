from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging
from typing import Optional, List

from app.database.database import get_db
from app.schemas.feeding_schema import FeedingCreate, FeedingUpdate, FeedingResponse, FeedingTodaySummary
from app.services import feeding_service, baby_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/feeding", tags=["Feeding"])

@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_feeding_log(feeding_in: FeedingCreate, family_id: Optional[int] = None, db: Session = Depends(get_db)):
    try:
        # Validate baby exists
        baby = baby_service.get_baby_by_id(db=db, baby_id=feeding_in.baby_id)
        if not baby:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Baby with ID {feeding_in.baby_id} not found."
            )
        
        # Validate family ownership
        if family_id is not None and baby.family_id != family_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Baby profile does not belong to this family."
            )
            
        db_feeding = feeding_service.create_feeding(db=db, feeding_in=feeding_in)
        logger.info(f"Successfully created feeding log ID: {db_feeding.id} for baby: {db_feeding.baby_id}")
        return {
            "success": True,
            "message": "Feeding log created successfully.",
            "data": FeedingResponse.model_validate(db_feeding)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating feeding log: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating feeding log."
        )

@router.get("/{baby_id}")
def get_feeding_history(baby_id: int, family_id: Optional[int] = None, db: Session = Depends(get_db)):
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
            
        feedings = feeding_service.get_feeding_history(db=db, baby_id=baby_id)
        return {
            "success": True,
            "message": "Feeding history retrieved successfully.",
            "data": [FeedingResponse.model_validate(f) for f in feedings]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching feeding history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching feeding history."
        )

@router.get("/today/{baby_id}")
def get_today_summary(baby_id: int, family_id: Optional[int] = None, db: Session = Depends(get_db)):
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
            
        summary = feeding_service.get_today_summary(db=db, baby_id=baby_id)
        
        # Serialize list of model instances in dict response manually before schema validation
        summary["feedings"] = [FeedingResponse.model_validate(f) for f in summary["feedings"]]
        
        return {
            "success": True,
            "message": "Today's feeding summary retrieved successfully.",
            "data": FeedingTodaySummary.model_validate(summary)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching today summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating feeding summary."
        )

@router.put("/{feeding_id}")
def update_feeding_log(feeding_id: int, feeding_in: FeedingUpdate, family_id: Optional[int] = None, db: Session = Depends(get_db)):
    try:
        db_feeding = feeding_service.get_feeding_by_id(db=db, feeding_id=feeding_id)
        if not db_feeding:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feeding log with ID {feeding_id} not found."
            )
            
        # Validate baby existence & family ownership
        baby = baby_service.get_baby_by_id(db=db, baby_id=db_feeding.baby_id)
        if family_id is not None and baby and baby.family_id != family_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Baby profile does not belong to this family."
            )
            
        updated = feeding_service.update_feeding(db=db, db_feeding=db_feeding, feeding_in=feeding_in)
        logger.info(f"Successfully updated feeding log ID: {feeding_id}")
        return {
            "success": True,
            "message": "Feeding log updated successfully.",
            "data": FeedingResponse.model_validate(updated)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating feeding log {feeding_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating feeding log."
        )

@router.delete("/{feeding_id}")
def delete_feeding_log(feeding_id: int, family_id: Optional[int] = None, db: Session = Depends(get_db)):
    try:
        db_feeding = feeding_service.get_feeding_by_id(db=db, feeding_id=feeding_id)
        if not db_feeding:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feeding log with ID {feeding_id} not found."
            )
            
        # Validate baby existence & family ownership
        baby = baby_service.get_baby_by_id(db=db, baby_id=db_feeding.baby_id)
        if family_id is not None and baby and baby.family_id != family_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Baby profile does not belong to this family."
            )
            
        feeding_service.delete_feeding(db=db, db_feeding=db_feeding)
        logger.info(f"Successfully deleted feeding log ID: {feeding_id}")
        return {
            "success": True,
            "message": "Feeding log deleted successfully.",
            "data": {}
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting feeding log {feeding_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting feeding log."
        )
