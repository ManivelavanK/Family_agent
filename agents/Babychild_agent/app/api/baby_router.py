from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging
from typing import Optional

from app.database.database import get_db
from app.schemas.baby_schema import BabyCreate, BabyUpdate, BabyResponse
from app.services import baby_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/baby", tags=["Baby"])

@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_baby_profile(baby_in: BabyCreate, db: Session = Depends(get_db)):
    try:
        db_baby = baby_service.create_baby(db=db, baby_in=baby_in)
        logger.info(f"Successfully created baby profile for ID: {db_baby.id}")
        return {
            "success": True,
            "message": "Baby profile created successfully.",
            "data": BabyResponse.model_validate(db_baby)
        }
    except Exception as e:
        logger.error(f"Error creating baby profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating baby profile."
        )

@router.get("/all")
def get_all_babies(family_id: Optional[int] = None, db: Session = Depends(get_db)):
    try:
        babies = baby_service.get_all_babies(db=db, family_id=family_id)
        return {
            "success": True,
            "message": "Babies list retrieved successfully.",
            "data": [BabyResponse.model_validate(b) for b in babies]
        }
    except Exception as e:
        logger.error(f"Error fetching babies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching babies list."
        )

@router.get("/{baby_id}")
def get_baby_details(baby_id: int, db: Session = Depends(get_db)):
    try:
        db_baby = baby_service.get_baby_by_id(db=db, baby_id=baby_id)
        if not db_baby:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Baby with ID {baby_id} not found."
            )
        return {
            "success": True,
            "message": "Baby details retrieved successfully.",
            "data": BabyResponse.model_validate(db_baby)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching baby profile {baby_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching baby details."
        )

@router.put("/{baby_id}")
def update_baby_profile(baby_id: int, baby_in: BabyUpdate, db: Session = Depends(get_db)):
    try:
        db_baby = baby_service.get_baby_by_id(db=db, baby_id=baby_id)
        if not db_baby:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Baby with ID {baby_id} not found."
            )
        updated_baby = baby_service.update_baby(db=db, db_baby=db_baby, baby_in=baby_in)
        logger.info(f"Successfully updated baby profile ID: {baby_id}")
        return {
            "success": True,
            "message": "Baby profile updated successfully.",
            "data": BabyResponse.model_validate(updated_baby)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating baby profile {baby_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating baby profile."
        )

@router.delete("/{baby_id}")
def delete_baby_profile(baby_id: int, db: Session = Depends(get_db)):
    try:
        db_baby = baby_service.get_baby_by_id(db=db, baby_id=baby_id)
        if not db_baby:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Baby with ID {baby_id} not found."
            )
        baby_service.delete_baby(db=db, db_baby=db_baby)
        logger.info(f"Successfully deleted baby profile ID: {baby_id}")
        return {
            "success": True,
            "message": "Baby profile deleted successfully.",
            "data": {}
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting baby profile {baby_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting baby profile."
        )
