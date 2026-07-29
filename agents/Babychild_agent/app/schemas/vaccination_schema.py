from pydantic import BaseModel, field_validator, ConfigDict
from datetime import date, datetime
from typing import Optional

class VaccinationBase(BaseModel):
    baby_id: int
    vaccine_name: str
    dose_number: Optional[int] = None
    due_date: date
    completed_date: Optional[date] = None
    status: str
    hospital: Optional[str] = None
    doctor_name: Optional[str] = None
    notes: Optional[str] = None

class VaccinationCreate(VaccinationBase):
    @field_validator("vaccine_name")
    @classmethod
    def vaccine_name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Vaccine name is required.")
        return v.strip()

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = ["pending", "completed", "missed"]
        if v not in allowed:
            raise ValueError(f"Status must be one of: {', '.join(allowed)}")
        return v

class VaccinationUpdate(BaseModel):
    vaccine_name: Optional[str] = None
    dose_number: Optional[int] = None
    due_date: Optional[date] = None
    completed_date: Optional[date] = None
    status: Optional[str] = None
    hospital: Optional[str] = None
    doctor_name: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("vaccine_name")
    @classmethod
    def vaccine_name_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Vaccine name is required.")
            return v.strip()
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = ["pending", "completed", "missed"]
            if v not in allowed:
                raise ValueError(f"Status must be one of: {', '.join(allowed)}")
        return v

class VaccinationResponse(VaccinationBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
