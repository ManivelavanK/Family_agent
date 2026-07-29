from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.assignment import Assignment
from pydantic import BaseModel
from datetime import date
from typing import Optional

router = APIRouter(prefix="/api/v1/assignments", tags=["Assignments"])

class AssignmentCreate(BaseModel):
    student_id: int
    subject_id: int
    title: str
    due_date: date
    priority: str = "Medium"
    description: Optional[str] = ""
    status: str = "Pending"
    actual_minutes_spent: Optional[int] = 0

class AssignmentUpdate(BaseModel):
    title: Optional[str] = None
    due_date: Optional[date] = None
    priority: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    actual_minutes_spent: Optional[int] = None

@router.get("")
def get_assignments(student_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Assignment)
    if student_id:
        query = query.filter(Assignment.student_id == student_id)
    return query.all()

@router.post("")
def create_assignment(payload: AssignmentCreate, db: Session = Depends(get_db)):
    new_assign = Assignment(**payload.dict())
    db.add(new_assign)
    db.commit()
    db.refresh(new_assign)
    return new_assign

@router.put("/{assignment_id}")
def update_assignment(assignment_id: int, payload: AssignmentUpdate, db: Session = Depends(get_db)):
    assign = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assign:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    for key, val in payload.dict(exclude_unset=True).items():
        setattr(assign, key, val)
        
    db.commit()
    db.refresh(assign)
    return assign

@router.delete("/{assignment_id}")
def delete_assignment(assignment_id: int, db: Session = Depends(get_db)):
    assign = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assign:
        raise HTTPException(status_code=404, detail="Assignment not found")
    db.delete(assign)
    db.commit()
    return {"status": "success", "message": "Assignment deleted"}
