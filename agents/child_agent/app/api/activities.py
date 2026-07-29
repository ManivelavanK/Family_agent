import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.activity import (
    ActivityCreate,
    ActivityResponse,
    AgendaDay,
)
from app.services import activity_service

router = APIRouter(tags=["Activity Scheduler"])


@router.post("/children/activities", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
def create_activity(activity: ActivityCreate, db: Session = Depends(get_db)):
    return activity_service.create_activity(db=db, activity_in=activity)


@router.get("/children/activities/{child_id}", response_model=List[ActivityResponse])
def get_activities(child_id: int, db: Session = Depends(get_db)):
    return activity_service.get_activities_by_child_id(db=db, child_id=child_id)


@router.put("/children/activities/{activity_id}", response_model=ActivityResponse)
def update_activity(activity_id: int, activity: ActivityCreate, db: Session = Depends(get_db)):
    db_act = activity_service.update_activity(db=db, activity_id=activity_id, activity_in=activity)
    if not db_act:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity with ID {activity_id} not found",
        )
    return db_act


@router.delete("/children/activities/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(activity_id: int, db: Session = Depends(get_db)):
    success = activity_service.delete_activity(db=db, activity_id=activity_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity with ID {activity_id} not found",
        )
    return None


@router.get("/children/agenda/{child_id}/today", response_model=List[AgendaDay])
def get_agenda_today(child_id: int, db: Session = Depends(get_db)):
    today = datetime.date.today()
    return activity_service.build_agenda_for_range(db=db, child_id=child_id, start_date=today, end_date=today)


@router.get("/children/agenda/{child_id}/week", response_model=List[AgendaDay])
def get_agenda_week(child_id: int, db: Session = Depends(get_db)):
    today = datetime.date.today()
    end_week = today + datetime.timedelta(days=6)
    return activity_service.build_agenda_for_range(db=db, child_id=child_id, start_date=today, end_date=end_week)
