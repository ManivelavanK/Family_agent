from pydantic import BaseModel, field_validator, ConfigDict
from datetime import datetime
from typing import Optional, List

class FeedingBase(BaseModel):
    baby_id: int
    feeding_type: str
    food_name: Optional[str] = None
    quantity_ml: Optional[float] = None
    duration_minutes: Optional[int] = None
    feeding_time: datetime
    notes: Optional[str] = None

class FeedingCreate(FeedingBase):
    @field_validator("feeding_type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        allowed = ["breast", "formula", "solid"]
        if v not in allowed:
            raise ValueError(f"Feeding type must be one of: {', '.join(allowed)}")
        return v

    @field_validator("quantity_ml")
    @classmethod
    def quantity_not_negative(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("Quantity cannot be negative.")
        return v

    @field_validator("duration_minutes")
    @classmethod
    def duration_not_negative(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError("Duration cannot be negative.")
        return v

class FeedingUpdate(BaseModel):
    feeding_type: Optional[str] = None
    food_name: Optional[str] = None
    quantity_ml: Optional[float] = None
    duration_minutes: Optional[int] = None
    feeding_time: Optional[datetime] = None
    notes: Optional[str] = None

    @field_validator("feeding_type")
    @classmethod
    def validate_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = ["breast", "formula", "solid"]
            if v not in allowed:
                raise ValueError(f"Feeding type must be one of: {', '.join(allowed)}")
        return v

    @field_validator("quantity_ml")
    @classmethod
    def quantity_not_negative(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("Quantity cannot be negative.")
        return v

    @field_validator("duration_minutes")
    @classmethod
    def duration_not_negative(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError("Duration cannot be negative.")
        return v

class FeedingResponse(FeedingBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FeedingTodaySummary(BaseModel):
    baby_id: int
    total_feedings: int
    total_quantity_ml: float
    feedings: List[FeedingResponse]
