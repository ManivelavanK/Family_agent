from datetime import date, time, datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# --- Schedule Item Schemas ---

class ScheduleItemBase(BaseModel):
    child_id: int
    day_of_week: str = Field(..., description="Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday")
    subject: str
    start_time: time
    end_time: time
    room: Optional[str] = None
    teacher: Optional[str] = Field(None, description="Teacher or Professor name")
    transport_info: Optional[str] = Field(None, description="Bus route/number or commute info")
    schedule_type: Optional[str] = Field(
        default="PERIOD",
        description="PERIOD, LECTURE, LAB, ASSEMBLY, BUS, CLUB, PROJECT, SCHOOL_ACTIVITY, COMMUTE"
    )
    education_stage: Optional[str] = Field(None, description="SCHOOL or COLLEGE")

class ScheduleItemCreate(ScheduleItemBase):
    pass

class ScheduleItemResponse(ScheduleItemBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# --- Holiday Calendar Schemas ---

class HolidayCalendarBase(BaseModel):
    child_id: int
    date: date
    title: str
    description: Optional[str] = None
    is_no_school: Optional[bool] = True

class HolidayCalendarCreate(HolidayCalendarBase):
    pass

class HolidayCalendarResponse(HolidayCalendarBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# --- Daily & Weekly Aggregated Schedule Responses ---

class TodayScheduleResponse(BaseModel):
    child_id: int
    date: date
    day_of_week: str
    is_holiday: bool
    holiday_info: Optional[HolidayCalendarResponse] = None
    education_stage: str
    schedule_items: List[ScheduleItemResponse] = Field(default_factory=list)
    bus_timings: List[ScheduleItemResponse] = Field(default_factory=list)
    summary: str


class WeekScheduleResponse(BaseModel):
    child_id: int
    education_stage: str
    monday: List[ScheduleItemResponse] = Field(default_factory=list)
    tuesday: List[ScheduleItemResponse] = Field(default_factory=list)
    wednesday: List[ScheduleItemResponse] = Field(default_factory=list)
    thursday: List[ScheduleItemResponse] = Field(default_factory=list)
    friday: List[ScheduleItemResponse] = Field(default_factory=list)
    saturday: List[ScheduleItemResponse] = Field(default_factory=list)
    sunday: List[ScheduleItemResponse] = Field(default_factory=list)
