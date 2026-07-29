from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.health import HealthRecord
from app.schemas.health_schema import HealthCreate, HealthUpdate

def create_health_record(db: Session, health_in: HealthCreate) -> HealthRecord:
    db_record = HealthRecord(
        baby_id=health_in.baby_id,
        temperature_c=health_in.temperature_c,
        heart_rate=health_in.heart_rate,
        symptoms=health_in.symptoms,
        medicine=health_in.medicine,
        doctor_name=health_in.doctor_name,
        notes=health_in.notes,
        visit_date=health_in.visit_date
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

def get_health_history(db: Session, baby_id: int) -> List[HealthRecord]:
    return db.query(HealthRecord).filter(HealthRecord.baby_id == baby_id).order_by(HealthRecord.visit_date.desc(), HealthRecord.id.desc()).all()

def get_health_summary(db: Session, baby_id: int) -> dict:
    records = db.query(HealthRecord).filter(HealthRecord.baby_id == baby_id).order_by(HealthRecord.visit_date.desc(), HealthRecord.id.desc()).all()
    
    total_records = len(records)
    if total_records == 0:
        return {
            "baby_id": baby_id,
            "total_records": 0,
            "latest_temperature_c": None,
            "latest_heart_rate": None,
            "latest_symptoms": None,
            "latest_medicine": None,
            "latest_visit_date": None
        }
        
    latest = records[0]
    return {
        "baby_id": baby_id,
        "total_records": total_records,
        "latest_temperature_c": latest.temperature_c,
        "latest_heart_rate": latest.heart_rate,
        "latest_symptoms": latest.symptoms,
        "latest_medicine": latest.medicine,
        "latest_visit_date": latest.visit_date
    }

def get_health_by_id(db: Session, health_id: int) -> Optional[HealthRecord]:
    return db.query(HealthRecord).filter(HealthRecord.id == health_id).first()

def update_health_record(db: Session, db_record: HealthRecord, health_in: HealthUpdate) -> HealthRecord:
    update_data = health_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_record, field, value)
    db.commit()
    db.refresh(db_record)
    return db_record

def delete_health_record(db: Session, db_record: HealthRecord) -> bool:
    db.delete(db_record)
    db.commit()
    return True
