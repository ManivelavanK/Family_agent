from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from app.models.sleep import SleepRecord
from app.schemas.sleep_schema import SleepCreate, SleepUpdate

def create_sleep(db: Session, sleep_in: SleepCreate) -> SleepRecord:
    duration = int((sleep_in.end_time - sleep_in.start_time).total_seconds() / 60)
    db_sleep = SleepRecord(
        baby_id=sleep_in.baby_id,
        sleep_type=sleep_in.sleep_type,
        start_time=sleep_in.start_time,
        end_time=sleep_in.end_time,
        duration_minutes=duration,
        quality=sleep_in.quality,
        notes=sleep_in.notes
    )
    db.add(db_sleep)
    db.commit()
    db.refresh(db_sleep)
    return db_sleep

def get_sleep_history(db: Session, baby_id: int) -> List[SleepRecord]:
    return db.query(SleepRecord).filter(SleepRecord.baby_id == baby_id).order_by(SleepRecord.start_time.desc()).all()

def get_sleep_summary(db: Session, baby_id: int) -> dict:
    records = db.query(SleepRecord).filter(SleepRecord.baby_id == baby_id).all()
    
    total_records = len(records)
    total_duration = sum(r.duration_minutes for r in records)
    avg_duration = float(total_duration / total_records) if total_records > 0 else 0.0
    
    type_dist = {"night_sleep": 0, "day_nap": 0}
    quality_dist = {"good": 0, "average": 0, "poor": 0}
    
    for r in records:
        if r.sleep_type in type_dist:
            type_dist[r.sleep_type] += 1
        else:
            type_dist[r.sleep_type] = 1
            
        if r.quality:
            if r.quality in quality_dist:
                quality_dist[r.quality] += 1
            else:
                quality_dist[r.quality] = 1
                
    return {
        "baby_id": baby_id,
        "total_sleep_records": total_records,
        "total_sleep_duration_minutes": total_duration,
        "average_duration_minutes": avg_duration,
        "sleep_type_distribution": type_dist,
        "quality_distribution": quality_dist
    }

def get_sleep_by_id(db: Session, sleep_id: int) -> Optional[SleepRecord]:
    return db.query(SleepRecord).filter(SleepRecord.id == sleep_id).first()

def update_sleep(db: Session, db_sleep: SleepRecord, sleep_in: SleepUpdate) -> SleepRecord:
    update_data = sleep_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_sleep, field, value)
        
    # Recalculate duration
    db_sleep.duration_minutes = int((db_sleep.end_time - db_sleep.start_time).total_seconds() / 60)
    
    db.commit()
    db.refresh(db_sleep)
    return db_sleep

def delete_sleep(db: Session, db_sleep: SleepRecord) -> bool:
    db.delete(db_sleep)
    db.commit()
    return True
