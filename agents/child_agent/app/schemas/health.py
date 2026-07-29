from datetime import date, time
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict

class HealthLogBase(BaseModel):
    child_id: int
    date: date
    height: Optional[float] = Field(None, ge=0.0)
    weight: Optional[float] = Field(None, ge=0.0)
    water_intake_ml: int = Field(0, ge=0)
    sleep_hours: float = Field(0.0, ge=0.0, le=24.0)
    sleep_time: Optional[time] = None
    wake_time: Optional[time] = None
    physical_activity_minutes: int = Field(0, ge=0)
    exercise_type: Optional[str] = None
    vaccinations: Optional[List[str]] = None
    health_notes: Optional[str] = None

class HealthLogCreate(HealthLogBase):
    pass

class HealthLogResponse(HealthLogBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class HealthReportResponse(BaseModel):
    child_id: int
    daily_summary: Dict[str, Any]
    weekly_averages: Dict[str, Any]
    sleep_consistency_percentage: float
    water_consistency_percentage: float
    activity_consistency_percentage: float
    routine_analysis_alerts: List[str]
