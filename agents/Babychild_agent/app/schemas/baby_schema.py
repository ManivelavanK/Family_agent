from pydantic import BaseModel, field_validator, ConfigDict
from datetime import date, datetime
from typing import Optional

class BabyBase(BaseModel):
    family_id: int
    name: str
    date_of_birth: date
    gender: Optional[str] = None
    birth_weight: Optional[float] = None
    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    parent_contact: Optional[str] = None

class BabyCreate(BabyBase):
    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Name cannot be empty.")
        return v.strip()

    @field_validator("birth_weight")
    @classmethod
    def birth_weight_not_negative(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("Birth weight cannot be negative.")
        return v

    @field_validator("date_of_birth")
    @classmethod
    def date_of_birth_not_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Date of birth cannot be a future date.")
        return v

class BabyUpdate(BaseModel):
    family_id: Optional[int] = None
    name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    birth_weight: Optional[float] = None
    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    parent_contact: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Name cannot be empty.")
            return v.strip()
        return v

    @field_validator("birth_weight")
    @classmethod
    def birth_weight_not_negative(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("Birth weight cannot be negative.")
        return v

    @field_validator("date_of_birth")
    @classmethod
    def date_of_birth_not_future(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v > date.today():
            raise ValueError("Date of birth cannot be a future date.")
        return v

class BabyResponse(BabyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
