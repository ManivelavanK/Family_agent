from pydantic import BaseModel, field_validator, ConfigDict
from datetime import date, datetime
from typing import Optional, List

class HealthBase(BaseModel):
    baby_id: int
    temperature_c: float
    heart_rate: Optional[int] = None
    symptoms: Optional[str] = None
    medicine: Optional[str] = None
    doctor_name: Optional[str] = None
    visit_date: date
    notes: Optional[str] = None

class HealthCreate(HealthBase):
    @field_validator("temperature_c")
    @classmethod
    def temp_not_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Temperature cannot be negative.")
        return v

    @field_validator("heart_rate")
    @classmethod
    def hr_must_be_positive(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError("Heart rate must be positive.")
        return v

    @field_validator("visit_date")
    @classmethod
    def visit_date_not_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Visit date cannot be a future date.")
        return v

class HealthUpdate(BaseModel):
    temperature_c: Optional[float] = None
    heart_rate: Optional[int] = None
    symptoms: Optional[str] = None
    medicine: Optional[str] = None
    doctor_name: Optional[str] = None
    visit_date: Optional[date] = None
    notes: Optional[str] = None

    @field_validator("temperature_c")
    @classmethod
    def temp_not_negative(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("Temperature cannot be negative.")
        return v

    @field_validator("heart_rate")
    @classmethod
    def hr_must_be_positive(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError("Heart rate must be positive.")
        return v

    @field_validator("visit_date")
    @classmethod
    def visit_date_not_future(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v > date.today():
            raise ValueError("Visit date cannot be a future date.")
        return v

class HealthResponse(HealthBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class HealthSummary(BaseModel):
    baby_id: int
    total_records: int
    latest_temperature_c: Optional[float] = None
    latest_heart_rate: Optional[int] = None
    latest_symptoms: Optional[str] = None
    latest_medicine: Optional[str] = None
    latest_visit_date: Optional[date] = None
