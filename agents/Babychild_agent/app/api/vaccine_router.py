from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
import logging
from typing import Optional, List

from app.database.database import get_db
from app.schemas.vaccination_schema import VaccinationCreate, VaccinationUpdate, VaccinationResponse
from app.services import vaccination_service, baby_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/vaccine", tags=["Vaccination Management"])

@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_vaccination(vaccination_in: VaccinationCreate, family_id: Optional[int] = None, db: Session = Depends(get_db)):
    try:
        # Validate baby exists
        baby = baby_service.get_baby_by_id(db=db, baby_id=vaccination_in.baby_id)
        if not baby:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Baby with ID {vaccination_in.baby_id} not found."
            )
            
        # Validate family ownership
        if family_id is not None and baby.family_id != family_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Baby profile does not belong to this family."
            )
            
        db_record = vaccination_service.create_vaccination(db=db, vaccination_in=vaccination_in)
        logger.info(f"Successfully created vaccination record ID: {db_record.id} for baby: {db_record.baby_id}")
        return {
            "success": True,
            "message": "Vaccination record created successfully.",
            "data": VaccinationResponse.model_validate(db_record)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating vaccination record: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating vaccination record."
        )

@router.get("/{baby_id}")
def get_vaccination_history(baby_id: int, family_id: Optional[int] = None, db: Session = Depends(get_db)):
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
            
        history = vaccination_service.get_vaccination_history(db=db, baby_id=baby_id)
        return {
            "success": True,
            "message": "Vaccination history retrieved successfully.",
            "data": [VaccinationResponse.model_validate(v) for v in history]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching vaccination history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching vaccination history."
        )

@router.get("/upcoming/{baby_id}")
def get_upcoming_vaccinations(baby_id: int, family_id: Optional[int] = None, db: Session = Depends(get_db)):
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
            
        upcoming = vaccination_service.get_upcoming_vaccinations(db=db, baby_id=baby_id)
        return {
            "success": True,
            "message": "Upcoming vaccinations retrieved successfully.",
            "data": [VaccinationResponse.model_validate(v) for v in upcoming]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching upcoming vaccinations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching upcoming vaccinations."
        )

@router.put("/complete/{vaccination_id}")
def complete_vaccination(vaccination_id: int, completed_date: Optional[date] = None, family_id: Optional[int] = None, db: Session = Depends(get_db)):
    try:
        db_record = vaccination_service.get_vaccination_by_id(db=db, vaccination_id=vaccination_id)
        if not db_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vaccination record with ID {vaccination_id} not found."
            )
            
        # Validate baby existence & family ownership
        baby = baby_service.get_baby_by_id(db=db, baby_id=db_record.baby_id)
        if family_id is not None and baby and baby.family_id != family_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Baby profile does not belong to this family."
            )
            
        updated = vaccination_service.complete_vaccination(db=db, db_vaccination=db_record, completed_date=completed_date)
        logger.info(f"Successfully completed vaccination ID: {vaccination_id}")
        return {
            "success": True,
            "message": "Vaccination completed successfully.",
            "data": VaccinationResponse.model_validate(updated)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing vaccination {vaccination_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while completing vaccination record."
        )

@router.delete("/{vaccination_id}")
def delete_vaccination(vaccination_id: int, family_id: Optional[int] = None, db: Session = Depends(get_db)):
    try:
        db_record = vaccination_service.get_vaccination_by_id(db=db, vaccination_id=vaccination_id)
        if not db_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vaccination record with ID {vaccination_id} not found."
            )
            
        # Validate baby existence & family ownership
        baby = baby_service.get_baby_by_id(db=db, baby_id=db_record.baby_id)
        if family_id is not None and baby and baby.family_id != family_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Baby profile does not belong to this family."
            )
            
        vaccination_service.delete_vaccination(db=db, db_vaccination=db_record)
        logger.info(f"Successfully deleted vaccination ID: {vaccination_id}")
        return {
            "success": True,
            "message": "Vaccination record deleted successfully.",
            "data": {}
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting vaccination {vaccination_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting vaccination record."
        )
