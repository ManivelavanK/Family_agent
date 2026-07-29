import datetime
from typing import List, Optional
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from app.models.calendar import CalendarEvent, EventStatus
from app.schemas.calendar import (
    CalendarEventCreate, CalendarEventUpdate,
    CalendarConflictInfo, CalendarConflictResponse
)

class CalendarService:
    @staticmethod
    def create_event(db: Session, event_in: CalendarEventCreate) -> CalendarEvent:
        db_event = CalendarEvent(**event_in.model_dump())
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        return db_event

    @staticmethod
    def get_event_by_id(db: Session, event_id: int) -> Optional[CalendarEvent]:
        return db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()

    @staticmethod
    def get_all_events(db: Session, skip: int = 0, limit: int = 100) -> List[CalendarEvent]:
        return db.query(CalendarEvent).order_by(CalendarEvent.start_datetime.asc()).offset(skip).limit(limit).all()

    @staticmethod
    def update_event(db: Session, event_id: int, event_in: CalendarEventUpdate) -> Optional[CalendarEvent]:
        db_event = CalendarService.get_event_by_id(db, event_id)
        if not db_event:
            return None
        
        update_data = event_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_event, field, value)
        
        db.commit()
        db.refresh(db_event)
        return db_event

    @staticmethod
    def delete_event(db: Session, event_id: int) -> bool:
        db_event = CalendarService.get_event_by_id(db, event_id)
        if not db_event:
            return False
        db.delete(db_event)
        db.commit()
        return True

    @staticmethod
    def get_upcoming_events(db: Session, limit: int = 10) -> List[CalendarEvent]:
        now = datetime.datetime.now(datetime.timezone.utc)
        return db.query(CalendarEvent).filter(
            CalendarEvent.end_datetime >= now,
            CalendarEvent.status != EventStatus.CANCELLED
        ).order_by(CalendarEvent.start_datetime.asc()).limit(limit).all()

    @staticmethod
    def get_events_by_date(db: Session, target_date: datetime.date) -> List[CalendarEvent]:
        start_of_day = datetime.datetime.combine(target_date, datetime.time.min)
        end_of_day = datetime.datetime.combine(target_date, datetime.time.max)
        return db.query(CalendarEvent).filter(
            and_(
                CalendarEvent.start_datetime <= end_of_day,
                CalendarEvent.end_datetime >= start_of_day,
                CalendarEvent.status != EventStatus.CANCELLED
            )
        ).order_by(CalendarEvent.start_datetime.asc()).all()

    @staticmethod
    def get_events_in_range(db: Session, start_date: datetime.date, end_date: datetime.date) -> List[CalendarEvent]:
        start_dt = datetime.datetime.combine(start_date, datetime.time.min)
        end_dt = datetime.datetime.combine(end_date, datetime.time.max)
        return db.query(CalendarEvent).filter(
            and_(
                CalendarEvent.start_datetime <= end_dt,
                CalendarEvent.end_datetime >= start_dt,
                CalendarEvent.status != EventStatus.CANCELLED
            )
        ).order_by(CalendarEvent.start_datetime.asc()).all()

    @staticmethod
    def check_conflicts(
        db: Session,
        start_datetime: datetime.datetime,
        end_datetime: datetime.datetime,
        exclude_event_id: Optional[int] = None
    ) -> CalendarConflictResponse:
        """
        Factual overlap condition: Event overlaps if (start_A < end_B) AND (end_A > start_B).
        Adjacent boundaries (e.g. 10:00-12:00 and 12:00-13:00) do NOT conflict.
        """
        query = db.query(CalendarEvent).filter(
            and_(
                CalendarEvent.start_datetime < end_datetime,
                CalendarEvent.end_datetime > start_datetime,
                CalendarEvent.status != EventStatus.CANCELLED
            )
        )
        if exclude_event_id:
            query = query.filter(CalendarEvent.id != exclude_event_id)

        overlapping_events = query.all()
        conflicts = [
            CalendarConflictInfo(
                event_id=e.id,
                title=e.title,
                event_type=e.event_type,
                start_datetime=e.start_datetime,
                end_datetime=e.end_datetime
            )
            for e in overlapping_events
        ]

        return CalendarConflictResponse(
            has_conflict=len(conflicts) > 0,
            conflicts=conflicts
        )
