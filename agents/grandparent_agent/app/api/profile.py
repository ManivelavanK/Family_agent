import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse
from app.schemas.response import APIResponse
from app.services.profile_service import get_profile, create_profile, update_profile, delete_profile

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/profile", tags=["Profile"])


@router.post("/", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def create_new_profile(profile_in: ProfileCreate, db: Session = Depends(get_db)):
    logger.info("Request received: Create profile")
    profile = create_profile(db, profile_in)
    logger.info("Database updated: Profile created/saved")
    return APIResponse(
        success=True,
        message="Profile created successfully",
        data=ProfileResponse.model_validate(profile)
    )


@router.get("/", response_model=APIResponse)
def read_profile(db: Session = Depends(get_db)):
    logger.info("Request received: Read profile")
    profile = get_profile(db)
    if not profile:
        logger.info("Profile not found in database")
        return APIResponse(
            success=False,
            message="Profile not found."
        )
    return APIResponse(
        success=True,
        message="Profile retrieved successfully",
        data=ProfileResponse.model_validate(profile)
    )


@router.put("/update", response_model=APIResponse)
def modify_profile(update_data: ProfileUpdate, db: Session = Depends(get_db)):
    logger.info("Request received: Update profile")
    try:
        profile = update_profile(db, update_data)
        logger.info("Database updated: Profile updated")
        return APIResponse(
            success=True,
            message="Profile updated successfully",
            data=ProfileResponse.model_validate(profile)
        )
    except ValueError as e:
        logger.warning("Profile update failed: %s", str(e))
        return APIResponse(
            success=False,
            message=str(e)
        )


@router.delete("/", response_model=APIResponse)
def remove_profile(db: Session = Depends(get_db)):
    logger.info("Request received: Delete profile")
    success = delete_profile(db)
    if not success:
        logger.warning("Profile deletion failed: Profile not found")
        return APIResponse(
            success=False,
            message="Profile not found."
        )
    logger.info("Database updated: Profile deleted")
    return APIResponse(
        success=True,
        message="Profile deleted successfully"
    )
