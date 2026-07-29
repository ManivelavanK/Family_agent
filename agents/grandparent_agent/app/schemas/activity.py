from pydantic import BaseModel, Field
from datetime import date as dt_date
from typing import Optional


class ActivityCreate(BaseModel):
    date: dt_date = Field(..., json_schema_extra={"example": "2026-07-27"})
    steps: int = Field(0, ge=0, json_schema_extra={"example": 6000})
    sleep_hours: float = Field(0.0, ge=0.0, json_schema_extra={"example": 7.5})
    activity_type: Optional[str] = Field(None, max_length=100, json_schema_extra={"example": "Walking"})
    duration_minutes: int = Field(0, ge=0, json_schema_extra={"example": 30})


class ActivityResponse(ActivityCreate):
    id: int

    class Config:
        from_attributes = True
