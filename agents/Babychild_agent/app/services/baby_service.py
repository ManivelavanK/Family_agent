from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.baby import Baby
from app.schemas.baby_schema import BabyCreate, BabyUpdate

def create_baby(db: Session, baby_in: BabyCreate) -> Baby:
    db_baby = Baby(
        family_id=baby_in.family_id,
        name=baby_in.name,
        date_of_birth=baby_in.date_of_birth,
        gender=baby_in.gender,
        birth_weight=baby_in.birth_weight,
        blood_group=baby_in.blood_group,
        allergies=baby_in.allergies,
        parent_contact=baby_in.parent_contact
    )
    db.add(db_baby)
    db.commit()
    db.refresh(db_baby)
    return db_baby

def get_baby_by_id(db: Session, baby_id: int) -> Optional[Baby]:
    return db.query(Baby).filter(Baby.id == baby_id).first()

def get_all_babies(db: Session, family_id: Optional[int] = None) -> List[Baby]:
    query = db.query(Baby)
    if family_id is not None:
        query = query.filter(Baby.family_id == family_id)
    return query.all()

def update_baby(db: Session, db_baby: Baby, baby_in: BabyUpdate) -> Baby:
    update_data = baby_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_baby, field, value)
    db.commit()
    db.refresh(db_baby)
    return db_baby

def delete_baby(db: Session, db_baby: Baby) -> bool:
    db.delete(db_baby)
    db.commit()
    return True
