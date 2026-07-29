from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.profile import ChildProfile
from app.schemas.profile import ChildProfileCreate, ChildProfileUpdate
from app.services.age_adaptation_service import classify_age_group

def create_child_profile(db: Session, profile_in: ChildProfileCreate) -> ChildProfile:
    # Auto-classify education stage
    edu_stage = classify_age_group(profile_in.age)
    
    db_profile = ChildProfile(
        family_id=profile_in.family_id,
        name=profile_in.name,
        date_of_birth=profile_in.date_of_birth,
        age=profile_in.age,
        gender=profile_in.gender,
        education_stage=edu_stage,
        class_or_year=profile_in.class_or_year,
        school_or_college=profile_in.school_or_college,
        blood_group=profile_in.blood_group,
        allergies=profile_in.allergies,
        emergency_contact=profile_in.emergency_contact,
        parent_contact=profile_in.parent_contact,
        interests=profile_in.interests,
        career_interest=profile_in.career_interest,
        daily_wake_time=profile_in.daily_wake_time,
        daily_sleep_time=profile_in.daily_sleep_time,
    )
    
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

def get_profile_by_id(db: Session, child_id: int) -> Optional[ChildProfile]:
    return db.query(ChildProfile).filter(ChildProfile.id == child_id).first()

def get_profiles_by_family_id(db: Session, family_id: str) -> List[ChildProfile]:
    return db.query(ChildProfile).filter(ChildProfile.family_id == family_id).all()

def get_profile_by_family_and_child_id(db: Session, family_id: str, child_id: int) -> Optional[ChildProfile]:
    return db.query(ChildProfile).filter(
        ChildProfile.family_id == family_id,
        ChildProfile.id == child_id
    ).first()

def update_child_profile(db: Session, child_id: int, profile_in: ChildProfileUpdate) -> Optional[ChildProfile]:
    db_profile = get_profile_by_id(db, child_id)
    if not db_profile:
        return None
    
    update_data = profile_in.model_dump(exclude_unset=True)
    
    # If age is updated, recalculate education_stage
    if "age" in update_data:
        update_data["education_stage"] = classify_age_group(update_data["age"])
        
    for field, value in update_data.items():
        setattr(db_profile, field, value)
        
    db.commit()
    db.refresh(db_profile)
    return db_profile

def delete_child_profile(db: Session, child_id: int) -> bool:
    db_profile = get_profile_by_id(db, child_id)
    if not db_profile:
        return False
    db.delete(db_profile)
    db.commit()
    return True
