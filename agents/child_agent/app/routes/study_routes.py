from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.study_session import StudySession
from app.models.progress import Progress
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/api/v1/study", tags=["Study Sessions"])

class StudySessionCreate(BaseModel):
    student_id: int
    subject_id: int
    topic: str
    start_time: datetime
    end_time: datetime
    focus_score: int = 100
    notes: Optional[str] = ""

@router.get("/sessions")
def get_study_sessions(student_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(StudySession)
    if student_id:
        query = query.filter(StudySession.student_id == student_id)
    return query.all()

@router.post("/sessions")
def record_session(payload: StudySessionCreate, db: Session = Depends(get_db)):
    duration = int((payload.end_time - payload.start_time).total_seconds() / 60)
    session = StudySession(
        student_id=payload.student_id,
        subject_id=payload.subject_id,
        topic=payload.topic,
        start_time=payload.start_time,
        end_time=payload.end_time,
        duration_minutes=max(1, duration),
        focus_score=payload.focus_score,
        notes=payload.notes
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    # Auto update progress log
    today = payload.start_time.date()
    prog = db.query(Progress).filter(Progress.student_id == payload.student_id, Progress.date == today).first()
    if not prog:
        prog = Progress(
            student_id=payload.student_id,
            date=today,
            study_hours=0.0,
            completed_assignments=0,
            goals_completed=0,
            consistency_score=85
        )
        db.add(prog)
    
    prog.study_hours += (session.duration_minutes / 60.0)
    # Check consistency streaks or score updates
    db.commit()
    return session
