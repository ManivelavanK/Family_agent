from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.goal import Goal
from pydantic import BaseModel
from datetime import date
from typing import Optional

router = APIRouter(prefix="/api/v1/goals", tags=["Goals"])

class GoalCreate(BaseModel):
    student_id: int
    title: str
    target_date: date
    description: Optional[str] = ""
    status: str = "In Progress"
    strategy: Optional[str] = ""
    progress_percentage: int = 0

class GoalUpdate(BaseModel):
    title: Optional[str] = None
    target_date: Optional[date] = None
    description: Optional[str] = None
    status: Optional[str] = None
    strategy: Optional[str] = None
    progress_percentage: Optional[int] = None

@router.get("")
def get_goals(student_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Goal)
    if student_id:
        query = query.filter(Goal.student_id == student_id)
    return query.all()

@router.post("")
def create_goal(payload: GoalCreate, db: Session = Depends(get_db)):
    new_goal = Goal(**payload.dict())
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)
    return new_goal

@router.put("/{goal_id}")
def update_goal(goal_id: int, payload: GoalUpdate, db: Session = Depends(get_db)):
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    for key, val in payload.dict(exclude_unset=True).items():
        setattr(goal, key, val)
        
    db.commit()
    db.refresh(goal)
    return goal

@router.delete("/{goal_id}")
def delete_goal(goal_id: int, db: Session = Depends(get_db)):
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    db.delete(goal)
    db.commit()
    return {"status": "success", "message": "Goal deleted"}
