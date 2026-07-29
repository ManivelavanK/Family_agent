from pydantic import BaseModel, field_validator, model_validator, ConfigDict
from datetime import datetime
from typing import Optional, Dict, List

class SleepBase(BaseModel):
    baby_id: int
    sleep_type: str
    start_time: datetime
    end_time: datetime
    quality: Optional[str] = None
    notes: Optional[str] = None

class SleepCreate(SleepBase):
    @field_validator("sleep_type")
    @classmethod
    def validate_sleep_type(cls, v: str) -> str:
        allowed = ["night_sleep", "day_nap"]
        if v not in allowed:
            raise ValueError(f"Sleep type must be one of: {', '.join(allowed)}")
        return v

    @field_validator("quality")
    @classmethod
    def validate_quality(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = ["good", "average", "poor"]
            if v not in allowed:
                raise ValueError(f"Quality must be one of: {', '.join(allowed)}")
        return v

    @model_validator(mode="after")
    def validate_time_range(self) -> "SleepCreate":
        if self.end_time < self.start_time:
            raise ValueError("End time cannot be before start time.")
        return self

class SleepUpdate(BaseModel):
    sleep_type: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    quality: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("sleep_type")
    @classmethod
    def validate_sleep_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = ["night_sleep", "day_nap"]
            if v not in allowed:
                raise ValueError(f"Sleep type must be one of: {', '.join(allowed)}")
        return v

    @field_validator("quality")
    @classmethod
    def validate_quality(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = ["good", "average", "poor"]
            if v not in allowed:
                raise ValueError(f"Quality must be one of: {', '.join(allowed)}")
        return v

    @model_validator(mode="after")
    def validate_time_range(self) -> "SleepUpdate":
        if self.start_time is not None and self.end_time is not None:
            if self.end_time < self.start_time:
                raise ValueError("End time cannot be before start time.")
        return self

class SleepResponse(SleepBase):
    id: int
    duration_minutes: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SleepSummary(BaseModel):
    baby_id: int
    total_sleep_records: int
    total_sleep_duration_minutes: int
    average_duration_minutes: float
    sleep_type_distribution: Dict[str, int]
    quality_distribution: Dict[str, int]
