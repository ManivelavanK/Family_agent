from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional
from app.models.vaccination import VaccinationRecord
from app.schemas.vaccination_schema import VaccinationCreate, VaccinationUpdate

def create_vaccination(db: Session, vaccination_in: VaccinationCreate) -> VaccinationRecord:
    db_record = VaccinationRecord(
        baby_id=vaccination_in.baby_id,
        vaccine_name=vaccination_in.vaccine_name,
        dose_number=vaccination_in.dose_number,
        due_date=vaccination_in.due_date,
        completed_date=vaccination_in.completed_date,
        status=vaccination_in.status,
        hospital=vaccination_in.hospital,
        doctor_name=vaccination_in.doctor_name,
        notes=vaccination_in.notes
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

def get_vaccination_history(db: Session, baby_id: int) -> List[VaccinationRecord]:
    return db.query(VaccinationRecord).filter(VaccinationRecord.baby_id == baby_id).order_by(VaccinationRecord.due_date.desc()).all()

def get_upcoming_vaccinations(db: Session, baby_id: int) -> List[VaccinationRecord]:
    return db.query(VaccinationRecord).filter(
        VaccinationRecord.baby_id == baby_id,
        VaccinationRecord.status == "pending",
        VaccinationRecord.due_date >= date.today()
    ).order_by(VaccinationRecord.due_date.asc()).all()

def get_vaccination_by_id(db: Session, vaccination_id: int) -> Optional[VaccinationRecord]:
    return db.query(VaccinationRecord).filter(VaccinationRecord.id == vaccination_id).first()

def complete_vaccination(db: Session, db_vaccination: VaccinationRecord, completed_date: Optional[date] = None) -> VaccinationRecord:
    db_vaccination.status = "completed"
    db_vaccination.completed_date = completed_date or date.today()
    db.commit()
    db.refresh(db_vaccination)
    return db_vaccination

def update_vaccination(db: Session, db_vaccination: VaccinationRecord, vaccination_in: VaccinationUpdate) -> VaccinationRecord:
    update_data = vaccination_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_vaccination, field, value)
    db.commit()
    db.refresh(db_vaccination)
    return db_vaccination

def delete_vaccination(db: Session, db_vaccination: VaccinationRecord) -> bool:
    db.delete(db_vaccination)
    db.commit()
    return True
