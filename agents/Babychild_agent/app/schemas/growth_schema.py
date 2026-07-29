from pydantic import BaseModel, field_validator, ConfigDict
from datetime import date, datetime
from typing import Optional, List

class GrowthBase(BaseModel):
    baby_id: int
    weight_kg: float
    height_cm: float
    head_circumference_cm: Optional[float] = None
    record_date: date

class GrowthCreate(GrowthBase):
    @field_validator("weight_kg")
    @classmethod
    def weight_not_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Weight cannot be negative.")
        return v

    @field_validator("height_cm")
    @classmethod
    def height_not_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Height cannot be negative.")
        return v

    @field_validator("head_circumference_cm")
    @classmethod
    def head_circumference_not_negative(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("Head circumference cannot be negative.")
        return v

    @field_validator("record_date")
    @classmethod
    def record_date_not_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Record date cannot be a future date.")
        return v

class GrowthUpdate(BaseModel):
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    head_circumference_cm: Optional[float] = None
    record_date: Optional[date] = None

    @field_validator("weight_kg")
    @classmethod
    def weight_not_negative(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("Weight cannot be negative.")
        return v

    @field_validator("height_cm")
    @classmethod
    def height_not_negative(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("Height cannot be negative.")
        return v

    @field_validator("head_circumference_cm")
    @classmethod
    def head_circumference_not_negative(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("Head circumference cannot be negative.")
        return v

    @field_validator("record_date")
    @classmethod
    def record_date_not_future(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v > date.today():
            raise ValueError("Record date cannot be a future date.")
        return v

class GrowthResponse(GrowthBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class GrowthSummary(BaseModel):
    baby_id: int
    total_records: int
    current_weight_kg: Optional[float] = None
    current_height_cm: Optional[float] = None
    current_head_circumference_cm: Optional[float] = None
    weight_change_kg: float
    height_change_cm: float

class GrowthPredictionResponse(BaseModel):
    current_weight: float
    predicted_weight: float
    growth_trend: str
