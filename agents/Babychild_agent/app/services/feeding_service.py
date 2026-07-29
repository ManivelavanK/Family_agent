from sqlalchemy.orm import Session
from datetime import datetime, date, time
from typing import List, Optional
from app.models.feeding import Feeding
from app.schemas.feeding_schema import FeedingCreate, FeedingUpdate

def create_feeding(db: Session, feeding_in: FeedingCreate) -> Feeding:
    db_feeding = Feeding(
        baby_id=feeding_in.baby_id,
        feeding_type=feeding_in.feeding_type,
        food_name=feeding_in.food_name,
        quantity_ml=feeding_in.quantity_ml,
        duration_minutes=feeding_in.duration_minutes,
        feeding_time=feeding_in.feeding_time,
        notes=feeding_in.notes
    )
    db.add(db_feeding)
    db.commit()
    db.refresh(db_feeding)
    return db_feeding

def get_feeding_history(db: Session, baby_id: int) -> List[Feeding]:
    return db.query(Feeding).filter(Feeding.baby_id == baby_id).order_by(Feeding.feeding_time.desc()).all()

def get_today_summary(db: Session, baby_id: int) -> dict:
    today_start = datetime.combine(date.today(), time.min)
    today_end = datetime.combine(date.today(), time.max)
    
    today_feedings = db.query(Feeding).filter(
        Feeding.baby_id == baby_id,
        Feeding.feeding_time >= today_start,
        Feeding.feeding_time <= today_end
    ).all()
    
    total_quantity = sum(f.quantity_ml for f in today_feedings if f.quantity_ml is not None)
    
    return {
        "baby_id": baby_id,
        "total_feedings": len(today_feedings),
        "total_quantity_ml": float(total_quantity),
        "feedings": today_feedings
    }

def get_feeding_by_id(db: Session, feeding_id: int) -> Optional[Feeding]:
    return db.query(Feeding).filter(Feeding.id == feeding_id).first()

def update_feeding(db: Session, db_feeding: Feeding, feeding_in: FeedingUpdate) -> Feeding:
    update_data = feeding_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_feeding, field, value)
    db.commit()
    db.refresh(db_feeding)
    return db_feeding

def delete_feeding(db: Session, db_feeding: Feeding) -> bool:
    db.delete(db_feeding)
    db.commit()
    return True
