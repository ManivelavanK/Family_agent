import logging
from sqlalchemy.orm import Session
from app.models.profile import Profile
from app.schemas.profile import ProfileCreate, ProfileUpdate

logger = logging.getLogger(__name__)


def get_profile(db: Session) -> Profile:
    """Gets the first profile in the database or returns None if empty."""
    return db.query(Profile).first()


def create_profile(db: Session, profile_in: ProfileCreate) -> Profile:
    existing = db.query(Profile).first()
    if existing:
        # If profile exists, update it instead of creating duplicates
        for field, value in profile_in.model_dump().items():
            setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        logger.info("Updated existing grandparent profile instead of recreating.")
        return existing

    new_profile = Profile(
        name=profile_in.name,
        age=profile_in.age,
        allergies=profile_in.allergies,
        medical_history=profile_in.medical_history,
        emergency_contact_name=profile_in.emergency_contact_name,
        emergency_contact_phone=profile_in.emergency_contact_phone
    )
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    logger.info("Created new grandparent profile.")
    return new_profile


def update_profile(db: Session, update_data: ProfileUpdate) -> Profile:
    profile = get_profile(db)
    if not profile:
        raise ValueError("Profile does not exist. Please create one first.")
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    logger.info("Updated grandparent profile.")
    return profile


def delete_profile(db: Session) -> bool:
    profile = get_profile(db)
    if not profile:
        return False
    db.delete(profile)
    db.commit()
    logger.info("Deleted grandparent profile.")
    return True
