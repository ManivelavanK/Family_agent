from datetime import date, time
from typing import List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict

class ChildProfileBase(BaseModel):
    family_id: str
    name: str
    date_of_birth: date
    age: int = Field(..., ge=0, le=100)
    gender: str
    class_or_year: Optional[str] = None
    school_or_college: Optional[str] = None
    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    emergency_contact: Optional[str] = None
    parent_contact: str
    interests: Optional[List[str]] = None
    career_interest: Optional[str] = None
    daily_wake_time: Optional[time] = None
    daily_sleep_time: Optional[time] = None

class ChildProfileCreate(ChildProfileBase):
    pass

class ChildProfileUpdate(BaseModel):
    family_id: Optional[str] = None
    name: Optional[str] = None
    date_of_birth: Optional[date] = None
    age: Optional[int] = Field(None, ge=0, le=100)
    gender: Optional[str] = None
    class_or_year: Optional[str] = None
    school_or_college: Optional[str] = None
    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    emergency_contact: Optional[str] = None
    parent_contact: Optional[str] = None
    interests: Optional[List[str]] = None
    career_interest: Optional[str] = None
    daily_wake_time: Optional[time] = None
    daily_sleep_time: Optional[time] = None

class ChildProfileResponse(ChildProfileBase):
    id: int
    education_stage: str

    model_config = ConfigDict(from_attributes=True)

class AdaptivePlanResponse(BaseModel):
    age_group: str
    education_stage: str
    recommended_study_duration: str
    recommended_sleep_duration: str
    recommended_screen_time_limit: str
    activity_recommendation: str
    parent_supervision_level: str
    financial_independence_level: str
    safety_monitoring_level: str
