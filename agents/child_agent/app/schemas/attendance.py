from datetime import date
from typing import Dict
from pydantic import BaseModel, Field, ConfigDict

class AttendanceBase(BaseModel):
    child_id: int
    date: date
    subject: str
    status: str = Field(..., description="Present, Absent, Leave")

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceResponse(AttendanceBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class AttendanceSummaryResponse(BaseModel):
    days_present: int
    days_absent: int
    days_on_leave: int
    attendance_percentage: float
    subject_wise_attendance: Dict[str, float]
    monthly_attendance: Dict[str, float]

class AttendanceRiskResponse(BaseModel):
    attendance_percentage: float
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    classes_can_miss: int
    classes_needed_to_recover: int
