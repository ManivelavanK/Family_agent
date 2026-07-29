from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.subject import Subject
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/v1/subjects", tags=["Subjects"])

class SubjectCreate(BaseModel):
    student_id: int
    name: str
    target_hours_per_week: int
    current_grade: Optional[str] = None
    color: Optional[str] = "#6366F1"

class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    target_hours_per_week: Optional[int] = None
    current_grade: Optional[str] = None
    color: Optional[str] = None

@router.get("")
def get_subjects(student_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Subject)
    if student_id:
        query = query.filter(Subject.student_id == student_id)
    return query.all()

@router.post("")
def create_subject(payload: SubjectCreate, db: Session = Depends(get_db)):
    new_sub = Subject(**payload.dict())
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)
    return new_sub

@router.put("/{subject_id}")
def update_subject(subject_id: int, payload: SubjectUpdate, db: Session = Depends(get_db)):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    for key, val in payload.dict(exclude_unset=True).items():
        setattr(subject, key, val)
        
    db.commit()
    db.refresh(subject)
    return subject

@router.delete("/{subject_id}")
def delete_subject(subject_id: int, db: Session = Depends(get_db)):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    db.delete(subject)
    db.commit()
    return {"status": "success", "message": "Subject deleted"}
