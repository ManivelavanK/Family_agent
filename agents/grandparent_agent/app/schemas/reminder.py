from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ReminderCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, json_schema_extra={"example": "Take Evening Medication"})
    trigger_time: datetime = Field(..., json_schema_extra={"example": "2026-07-27T18:00:00"})
    reminder_type: str = Field("General", description="e.g., Medicine, Appointment, Hydration", json_schema_extra={"example": "Medicine"})
    notes: Optional[str] = Field(None, json_schema_extra={"example": "Take Metformin 500mg with dinner"})


class ReminderResponse(BaseModel):
    id: str = Field(..., json_schema_extra={"example": "rem_1234"})
    title: str = Field(..., json_schema_extra={"example": "Take Evening Medication"})
    trigger_time: datetime = Field(..., json_schema_extra={"example": "2026-07-27T18:00:00"})
    reminder_type: str = Field(..., json_schema_extra={"example": "Medicine"})
    notes: Optional[str] = Field(None, json_schema_extra={"example": "Take Metformin 500mg"})
    is_active: bool = Field(..., json_schema_extra={"example": True})
