from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.student import Student
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/v1/students", tags=["Students"])

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    grade: Optional[str] = None
    learning_style: Optional[str] = None
    interests: Optional[List[str]] = None
    career_interest: Optional[str] = None
    weekly_target_hours: Optional[int] = None
    education_level: Optional[str] = None
    age: Optional[int] = None
    institution: Optional[str] = None
    year_of_study: Optional[str] = None
    profile_metadata: Optional[dict] = None

@router.get("")
def get_students(db: Session = Depends(get_db)):
    return db.query(Student).all()

@router.get("/{student_id}")
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.put("/{student_id}")
def update_student(student_id: int, payload: StudentUpdate, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    update_data = payload.dict(exclude_unset=True)
    for key, val in update_data.items():
        setattr(student, key, val)
        
    db.commit()
    db.refresh(student)
    return student

from app.services.digital_twin_service import update_academic_digital_twin

@router.get("/{student_id}/digital-twin")
def get_student_digital_twin(student_id: int, db: Session = Depends(get_db)):
    try:
        twin = update_academic_digital_twin(db, student_id)
        return twin
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
