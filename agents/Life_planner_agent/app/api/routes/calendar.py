import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.common import StandardResponse
from app.schemas.calendar import (
    CalendarEventCreate, CalendarEventUpdate, CalendarEventResponse,
    CalendarConflictResponse
)
from app.services.calendar_service import CalendarService

router = APIRouter(prefix="/calendar", tags=["Calendar"])

class ConflictCheckRequest(BaseModel):
    start_datetime: datetime.datetime
    end_datetime: datetime.datetime
    exclude_event_id: Optional[int] = None

@router.post("/events", response_model=StandardResponse[CalendarEventResponse], status_code=status.HTTP_201_CREATED)
def create_event(event_in: CalendarEventCreate, db: Session = Depends(get_db)):
    event = CalendarService.create_event(db, event_in)
    return StandardResponse(
        success=True,
        message="Calendar event created successfully",
        data=CalendarEventResponse.model_validate(event)
    )

@router.get("/events", response_model=StandardResponse[List[CalendarEventResponse]])
def get_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    events = CalendarService.get_all_events(db, skip=skip, limit=limit)
    return StandardResponse(
        success=True,
        message="Calendar events retrieved successfully",
        data=[CalendarEventResponse.model_validate(e) for e in events]
    )

@router.get("/upcoming", response_model=StandardResponse[List[CalendarEventResponse]])
def get_upcoming_events(limit: int = 10, db: Session = Depends(get_db)):
    events = CalendarService.get_upcoming_events(db, limit=limit)
    return StandardResponse(
        success=True,
        message="Upcoming calendar events retrieved successfully",
        data=[CalendarEventResponse.model_validate(e) for e in events]
    )

@router.get("/day/{target_date}", response_model=StandardResponse[List[CalendarEventResponse]])
def get_events_by_day(target_date: datetime.date, db: Session = Depends(get_db)):
    events = CalendarService.get_events_by_date(db, target_date)
    return StandardResponse(
        success=True,
        message=f"Calendar events for {target_date} retrieved successfully",
        data=[CalendarEventResponse.model_validate(e) for e in events]
    )

@router.get("/range", response_model=StandardResponse[List[CalendarEventResponse]])
def get_events_in_range(
    start_date: datetime.date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: datetime.date = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    if end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="end_date cannot be before start_date"
        )
    events = CalendarService.get_events_in_range(db, start_date, end_date)
    return StandardResponse(
        success=True,
        message="Calendar events in range retrieved successfully",
        data=[CalendarEventResponse.model_validate(e) for e in events]
    )

@router.post("/check-conflicts", response_model=StandardResponse[CalendarConflictResponse])
def check_conflicts(req: ConflictCheckRequest, db: Session = Depends(get_db)):
    conflict_res = CalendarService.check_conflicts(
        db=db,
        start_datetime=req.start_datetime,
        end_datetime=req.end_datetime,
        exclude_event_id=req.exclude_event_id
    )
    return StandardResponse(
        success=True,
        message="Conflict check completed",
        data=conflict_res
    )

@router.get("/events/{event_id}", response_model=StandardResponse[CalendarEventResponse])
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = CalendarService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Calendar event with ID {event_id} not found"
        )
    return StandardResponse(
        success=True,
        message="Calendar event retrieved successfully",
        data=CalendarEventResponse.model_validate(event)
    )

@router.put("/events/{event_id}", response_model=StandardResponse[CalendarEventResponse])
def update_event(event_id: int, event_in: CalendarEventUpdate, db: Session = Depends(get_db)):
    updated_event = CalendarService.update_event(db, event_id, event_in)
    if not updated_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Calendar event with ID {event_id} not found"
        )
    return StandardResponse(
        success=True,
        message="Calendar event updated successfully",
        data=CalendarEventResponse.model_validate(updated_event)
    )

@router.delete("/events/{event_id}", response_model=StandardResponse[dict])
def delete_event(event_id: int, db: Session = Depends(get_db)):
    success = CalendarService.delete_event(db, event_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Calendar event with ID {event_id} not found"
        )
    return StandardResponse(
        success=True,
        message="Calendar event deleted successfully",
        data={"event_id": event_id}
    )
