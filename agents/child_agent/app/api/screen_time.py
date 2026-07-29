from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.screen_time import (
    ScreenTimeCreate,
    ScreenTimeResponse,
    ScreenTimeTotalResponse,
    ScreenTimeAnalysisResponse,
)
from app.services import screen_time_service

router = APIRouter(prefix="/children/screen-time", tags=["Screen Time & Digital Wellness"])


@router.post("", response_model=ScreenTimeResponse, status_code=status.HTTP_201_CREATED)
def log_screen_time(log: ScreenTimeCreate, db: Session = Depends(get_db)):
    return screen_time_service.create_screen_time_log(db=db, log_in=log)


@router.get("/{child_id}/daily", response_model=ScreenTimeTotalResponse)
def get_daily(child_id: int, db: Session = Depends(get_db)):
    total = screen_time_service.get_daily_total(db=db, child_id=child_id)
    return ScreenTimeTotalResponse(total_minutes=total)


@router.get("/{child_id}/weekly", response_model=ScreenTimeTotalResponse)
def get_weekly(child_id: int, db: Session = Depends(get_db)):
    total = screen_time_service.get_weekly_total(db=db, child_id=child_id)
    return ScreenTimeTotalResponse(total_minutes=total)


@router.get("/{child_id}/monthly", response_model=ScreenTimeTotalResponse)
def get_monthly(child_id: int, db: Session = Depends(get_db)):
    total = screen_time_service.get_monthly_total(db=db, child_id=child_id)
    return ScreenTimeTotalResponse(total_minutes=total)


@router.get("/{child_id}/analysis", response_model=ScreenTimeAnalysisResponse)
def get_analysis(child_id: int, db: Session = Depends(get_db)):
    return screen_time_service.generate_screen_time_analysis(db=db, child_id=child_id)


@router.get("/{child_id}", response_model=List[ScreenTimeResponse])
def get_logs(child_id: int, db: Session = Depends(get_db)):
    return screen_time_service.get_logs_by_child_id(db=db, child_id=child_id)
