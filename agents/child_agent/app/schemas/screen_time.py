from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class ScreenTimeBase(BaseModel):
    child_id: int
    date: date
    mobile: int = Field(0, ge=0)
    gaming: int = Field(0, ge=0)
    tv: int = Field(0, ge=0)
    social_media: int = Field(0, ge=0)
    study_screen_time: int = Field(0, ge=0)
    other: int = Field(0, ge=0)
    late_night_minutes: int = Field(0, ge=0)

class ScreenTimeCreate(ScreenTimeBase):
    pass

class ScreenTimeResponse(ScreenTimeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class ScreenTimeTotalResponse(BaseModel):
    total_minutes: int

class ScreenTimeAnalysisResponse(BaseModel):
    total_screen_time: int
    entertainment_time: int
    study_time: int
    entertainment_study_ratio: float
    daily_average_entertainment: float
    weekly_trend: str
    alerts: List[str]
