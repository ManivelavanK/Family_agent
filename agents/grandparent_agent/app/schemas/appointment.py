from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class AppointmentCreate(BaseModel):
    doctor_name: str = Field(..., min_length=1, max_length=100, json_schema_extra={"example": "Dr. Sarah Smith"})
    specialty: str = Field(..., min_length=1, max_length=100, json_schema_extra={"example": "Cardiologist"})
    appointment_time: datetime = Field(..., json_schema_extra={"example": "2026-08-01T10:00:00"})
    location: Optional[str] = Field(None, max_length=200, json_schema_extra={"example": "General Hospital, Room 304"})
    notes: Optional[str] = Field(None, json_schema_extra={"example": "Routine checkup and blood pressure monitoring"})


class AppointmentResponse(AppointmentCreate):
    id: int

    class Config:
        from_attributes = True
