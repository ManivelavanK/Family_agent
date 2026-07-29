from pydantic import BaseModel, Field, ConfigDict
from datetime import date as datetime_date, time as datetime_time, datetime
from typing import List, Optional, Any
from enum import Enum

class CheckInStatus(str, Enum):
    SAFE = "SAFE"
    EXPECTED = "EXPECTED"
    LATE = "LATE"
    MISSED_CHECK_IN = "MISSED_CHECK_IN"
    EMERGENCY = "EMERGENCY"

class ChildSummaryItem(BaseModel):
    child_id: int
    name: str
    age: int
    education_stage: str
    attendance_rate: float
    pending_homework_count: int
    average_screen_time_hours: float
    saving_goals_progress: List[dict]

class ChildSummaryResponse(BaseModel):
    family_id: str
    summaries: List[ChildSummaryItem]

class ChildExpenseCreate(BaseModel):
    family_id: str
    child_id: int
    amount: float
    category: str  # Food, Transport, Education, Entertainment, Shopping, Gaming, Subscriptions, Friends, Emergency, Other
    description: Optional[str] = None
    date: Optional[datetime_date] = None

class ChildExpenseResponse(BaseModel):
    id: int
    family_id: str
    child_id: int
    amount: float
    category: str
    description: Optional[str]
    date: datetime_date

    model_config = ConfigDict(from_attributes=True)

class ChildEducationExpenseCreate(BaseModel):
    family_id: str
    child_id: int
    amount: float
    expense_type: str  # School fees, College fees, Books, Course fees, Transport expenses, Pocket-money patterns, Affordability requests
    description: Optional[str] = None
    date: Optional[datetime_date] = None

class ChildEducationExpenseResponse(BaseModel):
    id: int
    family_id: str
    child_id: int
    amount: float
    expense_type: str
    description: Optional[str]
    date: datetime_date

    model_config = ConfigDict(from_attributes=True)

class FamilyEventItem(BaseModel):
    child_id: int
    child_name: str
    event_type: str  # EXAM, ACTIVITY, SCHEDULE_ITEM, HOLIDAY
    title: str
    date: datetime_date
    start_time: Optional[datetime_time] = None
    end_time: Optional[datetime_time] = None
    location: Optional[str] = None
    description: Optional[str] = None

class FamilyEventsResponse(BaseModel):
    family_id: str
    events: List[FamilyEventItem]

class GroceryNeedItem(BaseModel):
    child_id: int
    child_name: str
    event_name: str
    date: datetime_date
    recommendation: str
    items: List[str]

class ChildGroceryNeedsResponse(BaseModel):
    family_id: str
    needs: List[GroceryNeedItem]

class ChildCheckInCreate(BaseModel):
    child_id: int
    date: Optional[datetime_date] = None
    expected_return_time: datetime_time
    actual_check_in_time: Optional[datetime_time] = None
    location_note: Optional[str] = None
    status: CheckInStatus = CheckInStatus.EXPECTED

class ChildCheckInResponse(BaseModel):
    id: int
    child_id: int
    date: datetime_date
    expected_return_time: datetime_time
    actual_check_in_time: Optional[datetime_time]
    location_note: Optional[str]
    status: CheckInStatus
    parent_notified: bool

    model_config = ConfigDict(from_attributes=True)

class ChildAlertCreate(BaseModel):
    child_id: int
    alert_type: str  # EMERGENCY, PANIC, LATE, ABSENT, NUTRITION_ALERT, BUDGET_ALERT
    message: str
    location_note: Optional[str] = None

class ChildAlertResponse(BaseModel):
    id: int
    child_id: int
    alert_type: str
    message: str
    channel: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
