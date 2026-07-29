from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.ai_dashboard import AIDailyDashboardResponse
from app.services import ai_dashboard_service

router = APIRouter(tags=["Children Daily Intelligence Dashboard"])

@router.get("/children/dashboard/{child_id}", response_model=AIDailyDashboardResponse)
def get_daily_dashboard(child_id: int, db: Session = Depends(get_db)):
    """
    GET /children/dashboard/{child_id}
    Aggregates profile, schedule, homework, exams, attendance, health logs, pocket money, safety status, 
    notifications, ML predictions, AI recommendations, and AI daily briefings into a structured dashboard.
    """
    try:
        return ai_dashboard_service.generate_ai_daily_dashboard(db=db, child_id=child_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

