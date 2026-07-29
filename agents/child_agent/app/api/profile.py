from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.profile import (
    ChildProfileCreate,
    ChildProfileUpdate,
    ChildProfileResponse,
    AdaptivePlanResponse,
)
from app.services import profile_service, age_adaptation_service

router = APIRouter(prefix="/children/profile", tags=["Child Profile"])


@router.post("", response_model=ChildProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(profile: ChildProfileCreate, db: Session = Depends(get_db)):
    return profile_service.create_child_profile(db=db, profile_in=profile)


@router.get("/{family_id}", response_model=List[ChildProfileResponse])
def get_profiles_by_family(family_id: str, db: Session = Depends(get_db)):
    return profile_service.get_profiles_by_family_id(db=db, family_id=family_id)


@router.get("/{child_id}/adaptive-plan", response_model=AdaptivePlanResponse)
def get_adaptive_plan(child_id: int, db: Session = Depends(get_db)):
    db_profile = profile_service.get_profile_by_id(db=db, child_id=child_id)
    if not db_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child profile with ID {child_id} not found",
        )
    recommendations = age_adaptation_service.get_adaptive_recommendations(
        age=db_profile.age, education_stage=db_profile.education_stage
    )
    return recommendations


@router.get("/{family_id}/{child_id}", response_model=ChildProfileResponse)
def get_profile_by_family_and_child(family_id: str, child_id: int, db: Session = Depends(get_db)):
    db_profile = profile_service.get_profile_by_family_and_child_id(
        db=db, family_id=family_id, child_id=child_id
    )
    if not db_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child profile with ID {child_id} not found in family {family_id}",
        )
    return db_profile


@router.put("/{child_id}", response_model=ChildProfileResponse)
def update_profile(child_id: int, profile: ChildProfileUpdate, db: Session = Depends(get_db)):
    db_profile = profile_service.update_child_profile(db=db, child_id=child_id, profile_in=profile)
    if not db_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child profile with ID {child_id} not found",
        )
    return db_profile


@router.delete("/{child_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile(child_id: int, db: Session = Depends(get_db)):
    success = profile_service.delete_child_profile(db=db, child_id=child_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child profile with ID {child_id} not found",
        )
    return None

