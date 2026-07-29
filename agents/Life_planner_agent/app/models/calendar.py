import enum
import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Enum, ForeignKey, Boolean
)
from sqlalchemy.orm import relationship as db_relationship
from app.database.session import Base

class EventType(str, enum.Enum):
    FAMILY_EVENT = "FAMILY_EVENT"
    BIRTHDAY = "BIRTHDAY"
    ANNIVERSARY = "ANNIVERSARY"
    FUNCTION = "FUNCTION"
    TRAVEL = "TRAVEL"
    APPOINTMENT = "APPOINTMENT"
    STUDY_EXAM = "STUDY_EXAM"
    GUEST_VISIT = "GUEST_VISIT"
    PERSONAL = "PERSONAL"
    REMINDER = "REMINDER"
    OTHER = "OTHER"

class EventStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"

class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    event_type = Column(Enum(EventType), nullable=False, default=EventType.OTHER)
    start_datetime = Column(DateTime(timezone=True), nullable=False, index=True)
    end_datetime = Column(DateTime(timezone=True), nullable=False, index=True)
    all_day = Column(Boolean, nullable=False, default=False)
    location = Column(String(255), nullable=True)
    status = Column(Enum(EventStatus), nullable=False, default=EventStatus.SCHEDULED)
    priority = Column(String(50), nullable=True, default="MEDIUM")
    source = Column(String(100), nullable=True, default="USER")
    plan_id = Column(Integer, ForeignKey("plans.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    plan = db_relationship("Plan", backref="calendar_events")
