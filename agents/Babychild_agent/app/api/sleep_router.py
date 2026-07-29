from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging
from typing import Optional, List

from app.database.database import get_db
from app.schemas.sleep_schema import SleepCreate, SleepUpdate, SleepResponse, SleepSummary
from app.services import sleep_service, baby_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/sleep", tags=["Sleep"])

@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_sleep_log(sleep_in: SleepCreate, family_id: Optional[int] = None, db: Session = Depends(get_db)):
    try:
        # Validate baby exists
        baby = baby_service.get_baby_by_id(db=db, baby_id=sleep_in.baby_id)
        if not baby:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Baby with ID {sleep_in.baby_id} not found."
            )
            
        # Validate family ownership
        if family_id is not None and baby.family_id != family_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Baby profile does not belong to this family."
            )
            
        db_sleep = sleep_service.create_sleep(db=db, sleep_in=sleep_in)
        logger.info(f"Successfully created sleep log ID: {db_sleep.id} for baby: {db_sleep.baby_id}")
        return {
            "success": True,
            "message": "Sleep log created successfully.",
            "data": SleepResponse.model_validate(db_sleep)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating sleep log: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating sleep log."
        )

@router.get("/{baby_id}")
def get_sleep_history(baby_id: int, family_id: Optional[int] = None, db: Session = Depends(get_db)):
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
            
        history = sleep_service.get_sleep_history(db=db, baby_id=baby_id)
        return {
            "success": True,
            "message": "Sleep history retrieved successfully.",
            "data": [SleepResponse.model_validate(s) for s in history]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching sleep history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching sleep history."
        )

@router.get("/summary/{baby_id}")
def get_sleep_summary(baby_id: int, family_id: Optional[int] = None, db: Session = Depends(get_db)):
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
            
        summary = sleep_service.get_sleep_summary(db=db, baby_id=baby_id)
        return {
            "success": True,
            "message": "Sleep summary retrieved successfully.",
            "data": SleepSummary.model_validate(summary)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching sleep summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating sleep summary."
        )

@router.put("/{sleep_id}")
def update_sleep_log(sleep_id: int, sleep_in: SleepUpdate, family_id: Optional[int] = None, db: Session = Depends(get_db)):
    try:
        db_sleep = sleep_service.get_sleep_by_id(db=db, sleep_id=sleep_id)
        if not db_sleep:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sleep record with ID {sleep_id} not found."
            )
            
        # Validate baby existence & family ownership
        baby = baby_service.get_baby_by_id(db=db, baby_id=db_sleep.baby_id)
        if family_id is not None and baby and baby.family_id != family_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Baby profile does not belong to this family."
            )
            
        updated = sleep_service.update_sleep(db=db, db_sleep=db_sleep, sleep_in=sleep_in)
        logger.info(f"Successfully updated sleep log ID: {sleep_id}")
        return {
            "success": True,
            "message": "Sleep log updated successfully.",
            "data": SleepResponse.model_validate(updated)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating sleep log {sleep_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating sleep log."
        )

@router.delete("/{sleep_id}")
def delete_sleep_log(sleep_id: int, family_id: Optional[int] = None, db: Session = Depends(get_db)):
    try:
        db_sleep = sleep_service.get_sleep_by_id(db=db, sleep_id=sleep_id)
        if not db_sleep:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sleep record with ID {sleep_id} not found."
            )
            
        # Validate baby existence & family ownership
        baby = baby_service.get_baby_by_id(db=db, baby_id=db_sleep.baby_id)
        if family_id is not None and baby and baby.family_id != family_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Baby profile does not belong to this family."
            )
            
        sleep_service.delete_sleep(db=db, db_sleep=db_sleep)
        logger.info(f"Successfully deleted sleep log ID: {sleep_id}")
        return {
            "success": True,
            "message": "Sleep log deleted successfully.",
            "data": {}
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting sleep log {sleep_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting sleep log."
        )
