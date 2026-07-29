import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.models.calendar import EventType, EventStatus

class CalendarEventBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    event_type: EventType = EventType.OTHER
    start_datetime: datetime.datetime
    end_datetime: datetime.datetime
    all_day: bool = False
    location: Optional[str] = Field(None, max_length=255)
    status: EventStatus = EventStatus.SCHEDULED
    priority: Optional[str] = Field("MEDIUM", max_length=50)
    source: Optional[str] = Field("USER", max_length=100)
    plan_id: Optional[int] = None

    @model_validator(mode="after")
    def validate_datetimes(self):
        if self.end_datetime <= self.start_datetime:
            raise ValueError("end_datetime must be strictly after start_datetime")
        return self

class CalendarEventCreate(CalendarEventBase):
    pass

class CalendarEventUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    event_type: Optional[EventType] = None
    start_datetime: Optional[datetime.datetime] = None
    end_datetime: Optional[datetime.datetime] = None
    all_day: Optional[bool] = None
    location: Optional[str] = Field(None, max_length=255)
    status: Optional[EventStatus] = None
    priority: Optional[str] = Field(None, max_length=50)
    source: Optional[str] = Field(None, max_length=100)
    plan_id: Optional[int] = None

    @model_validator(mode="after")
    def validate_datetimes(self):
        if self.start_datetime and self.end_datetime and self.end_datetime <= self.start_datetime:
            raise ValueError("end_datetime must be strictly after start_datetime")
        return self

class CalendarEventResponse(CalendarEventBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class CalendarConflictInfo(BaseModel):
    event_id: int
    title: str
    event_type: EventType
    start_datetime: datetime.datetime
    end_datetime: datetime.datetime

class CalendarConflictResponse(BaseModel):
    has_conflict: bool
    conflicts: List[CalendarConflictInfo] = []
