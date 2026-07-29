from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class VitalsCreate(BaseModel):
    blood_pressure_systolic: int = Field(..., ge=50, le=250, json_schema_extra={"example": 120})
    blood_pressure_diastolic: int = Field(..., ge=30, le=150, json_schema_extra={"example": 80})
    blood_sugar: float = Field(..., ge=20.0, le=600.0, json_schema_extra={"example": 95.5})
    heart_rate: int = Field(..., ge=30, le=220, json_schema_extra={"example": 72})
    temperature: Optional[float] = Field(None, ge=90.0, le=110.0, json_schema_extra={"example": 98.6})


class VitalsResponse(VitalsCreate):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
