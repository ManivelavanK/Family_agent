from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging
from typing import Optional, List

from app.database.database import get_db
from app.schemas.health_schema import HealthCreate, HealthUpdate, HealthResponse, HealthSummary
from app.services import health_service, baby_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/health", tags=["Health Monitoring"])

@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_health_record(health_in: HealthCreate, family_id: Optional[int] = None, db: Session = Depends(get_db)):
    try:
        # Validate baby exists
        baby = baby_service.get_baby_by_id(db=db, baby_id=health_in.baby_id)
        if not baby:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Baby with ID {health_in.baby_id} not found."
            )
            
        # Validate family ownership
        if family_id is not None and baby.family_id != family_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Baby profile does not belong to this family."
            )
            
        db_record = health_service.create_health_record(db=db, health_in=health_in)
        logger.info(f"Successfully created health record ID: {db_record.id} for baby: {db_record.baby_id}")
        return {
            "success": True,
            "message": "Health record created successfully.",
            "data": HealthResponse.model_validate(db_record)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating health record: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating health record."
        )

@router.get("/{baby_id}")
def get_health_history(baby_id: int, family_id: Optional[int] = None, db: Session = Depends(get_db)):
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
            
        history = health_service.get_health_history(db=db, baby_id=baby_id)
        return {
            "success": True,
            "message": "Health history retrieved successfully.",
            "data": [HealthResponse.model_validate(h) for h in history]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching health history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching health history."
        )

@router.get("/summary/{baby_id}")
def get_health_summary(baby_id: int, family_id: Optional[int] = None, db: Session = Depends(get_db)):
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
            
        summary = health_service.get_health_summary(db=db, baby_id=baby_id)
        return {
            "success": True,
            "message": "Health summary retrieved successfully.",
            "data": HealthSummary.model_validate(summary)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching health summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating health summary."
        )

@router.put("/{health_id}")
def update_health_record(health_id: int, health_in: HealthUpdate, family_id: Optional[int] = None, db: Session = Depends(get_db)):
    try:
        db_record = health_service.get_health_by_id(db=db, health_id=health_id)
        if not db_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Health record with ID {health_id} not found."
            )
            
        # Validate baby existence & family ownership
        baby = baby_service.get_baby_by_id(db=db, baby_id=db_record.baby_id)
        if family_id is not None and baby and baby.family_id != family_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Baby profile does not belong to this family."
            )
            
        updated = health_service.update_health_record(db=db, db_record=db_record, health_in=health_in)
        logger.info(f"Successfully updated health record ID: {health_id}")
        return {
            "success": True,
            "message": "Health record updated successfully.",
            "data": HealthResponse.model_validate(updated)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating health record {health_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating health record."
        )

@router.delete("/{health_id}")
def delete_health_record(health_id: int, family_id: Optional[int] = None, db: Session = Depends(get_db)):
    try:
        db_record = health_service.get_health_by_id(db=db, health_id=health_id)
        if not db_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Health record with ID {health_id} not found."
            )
            
        # Validate baby existence & family ownership
        baby = baby_service.get_baby_by_id(db=db, baby_id=db_record.baby_id)
        if family_id is not None and baby and baby.family_id != family_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Baby profile does not belong to this family."
            )
            
        health_service.delete_health_record(db=db, db_record=db_record)
        logger.info(f"Successfully deleted health record ID: {health_id}")
        return {
            "success": True,
            "message": "Health record deleted successfully.",
            "data": {}
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting health record {health_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting health record."
        )
