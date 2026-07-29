from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.progress import Progress
from typing import Optional

router = APIRouter(prefix="/api/v1/progress", tags=["Progress Analytics"])

@router.get("")
def get_progress_logs(student_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Progress)
    if student_id:
        query = query.filter(Progress.student_id == student_id)
    return query.order_by(Progress.date.asc()).all()
