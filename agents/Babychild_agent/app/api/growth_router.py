from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging
from typing import Optional, List

from app.database.database import get_db
from app.schemas.growth_schema import GrowthCreate, GrowthUpdate, GrowthResponse, GrowthSummary, GrowthPredictionResponse
from app.services import growth_service, baby_service
from app.ml import growth_prediction

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/growth", tags=["Growth"])

@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_growth(growth_in: GrowthCreate, family_id: Optional[int] = None, db: Session = Depends(get_db)):
    try:
        # Validate baby exists
        baby = baby_service.get_baby_by_id(db=db, baby_id=growth_in.baby_id)
        if not baby:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Baby with ID {growth_in.baby_id} not found."
            )
            
        # Validate family ownership
        if family_id is not None and baby.family_id != family_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Baby profile does not belong to this family."
            )
            
        db_record = growth_service.create_growth_record(db=db, growth_in=growth_in)
        logger.info(f"Successfully created growth record ID: {db_record.id} for baby: {db_record.baby_id}")
        return {
            "success": True,
            "message": "Growth record created successfully.",
            "data": GrowthResponse.model_validate(db_record)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating growth record: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating growth record."
        )

@router.get("/{baby_id}")
def get_growth_history(baby_id: int, family_id: Optional[int] = None, db: Session = Depends(get_db)):
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
            
        history = growth_service.get_growth_history(db=db, baby_id=baby_id)
        return {
            "success": True,
            "message": "Growth history retrieved successfully.",
            "data": [GrowthResponse.model_validate(g) for g in history]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching growth history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching growth history."
        )

@router.get("/summary/{baby_id}")
def get_growth_summary(baby_id: int, family_id: Optional[int] = None, db: Session = Depends(get_db)):
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
            
        summary = growth_service.get_growth_summary(db=db, baby_id=baby_id)
        return {
            "success": True,
            "message": "Growth summary retrieved successfully.",
            "data": GrowthSummary.model_validate(summary)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching growth summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating growth summary."
        )

@router.put("/{growth_id}")
def update_growth_record(growth_id: int, growth_in: GrowthUpdate, family_id: Optional[int] = None, db: Session = Depends(get_db)):
    try:
        db_record = growth_service.get_growth_by_id(db=db, growth_id=growth_id)
        if not db_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Growth record with ID {growth_id} not found."
            )
            
        # Validate baby existence & family ownership
        baby = baby_service.get_baby_by_id(db=db, baby_id=db_record.baby_id)
        if family_id is not None and baby and baby.family_id != family_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Baby profile does not belong to this family."
            )
            
        updated = growth_service.update_growth_record(db=db, db_record=db_record, growth_in=growth_in)
        logger.info(f"Successfully updated growth record ID: {growth_id}")
        return {
            "success": True,
            "message": "Growth record updated successfully.",
            "data": GrowthResponse.model_validate(updated)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating growth record {growth_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating growth record."
        )

@router.delete("/{growth_id}")
def delete_growth_record(growth_id: int, family_id: Optional[int] = None, db: Session = Depends(get_db)):
    try:
        db_record = growth_service.get_growth_by_id(db=db, growth_id=growth_id)
        if not db_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Growth record with ID {growth_id} not found."
            )
            
        # Validate baby existence & family ownership
        baby = baby_service.get_baby_by_id(db=db, baby_id=db_record.baby_id)
        if family_id is not None and baby and baby.family_id != family_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Baby profile does not belong to this family."
            )
            
        growth_service.delete_growth_record(db=db, db_record=db_record)
        logger.info(f"Successfully deleted growth record ID: {growth_id}")
        return {
            "success": True,
            "message": "Growth record deleted successfully.",
            "data": {}
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting growth record {growth_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting growth record."
        )

@router.post("/predict/{baby_id}")
def predict_weight(baby_id: int, family_id: Optional[int] = None, db: Session = Depends(get_db)):
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
            
        history = growth_service.get_growth_history(db=db, baby_id=baby_id)
        prediction = growth_prediction.predict_next_weight(history)
        return {
            "success": True,
            "message": "ML weight prediction generated successfully.",
            "data": GrowthPredictionResponse.model_validate(prediction)
        }
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error predicting growth for baby {baby_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating weight prediction."
        )
