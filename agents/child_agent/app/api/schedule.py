from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.schedule import (
    ScheduleItemCreate,
    ScheduleItemResponse,
    HolidayCalendarCreate,
    HolidayCalendarResponse,
    TodayScheduleResponse,
    WeekScheduleResponse,
)
from app.services import schedule_service

router = APIRouter(tags=["Schedule Agent"])


# --- Schedule APIs ---

@router.post("/children/schedule", response_model=ScheduleItemResponse, status_code=status.HTTP_201_CREATED)
def create_schedule_item(item: ScheduleItemCreate, db: Session = Depends(get_db)):
    return schedule_service.create_schedule_item(db=db, item_in=item)


@router.get("/children/schedule/{child_id}", response_model=List[ScheduleItemResponse])
def get_child_schedule(child_id: int, db: Session = Depends(get_db)):
    return schedule_service.get_child_schedule(db=db, child_id=child_id)


@router.get("/children/schedule/{child_id}/today", response_model=TodayScheduleResponse)
def get_today_schedule(child_id: int, target_date: Optional[str] = None, db: Session = Depends(get_db)):
    eval_d = None
    if target_date:
        try:
            eval_d = date.fromisoformat(target_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="target_date must be in YYYY-MM-DD format"
            )
    return schedule_service.generate_today_schedule(db=db, child_id=child_id, target_date=eval_d)


@router.get("/children/schedule/{child_id}/week", response_model=WeekScheduleResponse)
def get_week_schedule(child_id: int, db: Session = Depends(get_db)):
    return schedule_service.generate_week_schedule(db=db, child_id=child_id)


@router.delete("/children/schedule/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule_item(item_id: int, db: Session = Depends(get_db)):
    success = schedule_service.delete_schedule_item(db=db, item_id=item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule item ID {item_id} not found"
        )
    return None


# --- Holiday Calendar APIs ---

@router.post("/children/schedule/holiday", response_model=HolidayCalendarResponse, status_code=status.HTTP_201_CREATED)
def add_holiday(holiday: HolidayCalendarCreate, db: Session = Depends(get_db)):
    return schedule_service.add_holiday(db=db, holiday_in=holiday)


@router.get("/children/schedule/{child_id}/holidays", response_model=List[HolidayCalendarResponse])
def get_holidays(child_id: int, db: Session = Depends(get_db)):
    return schedule_service.get_holidays(db=db, child_id=child_id)
