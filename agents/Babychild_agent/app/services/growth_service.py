from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.growth import GrowthRecord
from app.schemas.growth_schema import GrowthCreate, GrowthUpdate

def create_growth_record(db: Session, growth_in: GrowthCreate) -> GrowthRecord:
    db_record = GrowthRecord(
        baby_id=growth_in.baby_id,
        weight_kg=growth_in.weight_kg,
        height_cm=growth_in.height_cm,
        head_circumference_cm=growth_in.head_circumference_cm,
        record_date=growth_in.record_date
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

def get_growth_history(db: Session, baby_id: int) -> List[GrowthRecord]:
    return db.query(GrowthRecord).filter(GrowthRecord.baby_id == baby_id).order_by(GrowthRecord.record_date.desc()).all()

def get_growth_summary(db: Session, baby_id: int) -> dict:
    records = db.query(GrowthRecord).filter(GrowthRecord.baby_id == baby_id).order_by(GrowthRecord.record_date.asc()).all()
    
    total_records = len(records)
    if total_records == 0:
        return {
            "baby_id": baby_id,
            "total_records": 0,
            "current_weight_kg": None,
            "current_height_cm": None,
            "current_head_circumference_cm": None,
            "weight_change_kg": 0.0,
            "height_change_cm": 0.0
        }
        
    oldest = records[0]
    latest = records[-1]
    
    return {
        "baby_id": baby_id,
        "total_records": total_records,
        "current_weight_kg": latest.weight_kg,
        "current_height_cm": latest.height_cm,
        "current_head_circumference_cm": latest.head_circumference_cm,
        "weight_change_kg": round(latest.weight_kg - oldest.weight_kg, 2),
        "height_change_cm": round(latest.height_cm - oldest.height_cm, 2)
    }

def get_growth_by_id(db: Session, growth_id: int) -> Optional[GrowthRecord]:
    return db.query(GrowthRecord).filter(GrowthRecord.id == growth_id).first()

def update_growth_record(db: Session, db_record: GrowthRecord, growth_in: GrowthUpdate) -> GrowthRecord:
    update_data = growth_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_record, field, value)
    db.commit()
    db.refresh(db_record)
    return db_record

def delete_growth_record(db: Session, db_record: GrowthRecord) -> bool:
    db.delete(db_record)
    db.commit()
    return True
