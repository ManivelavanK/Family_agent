from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


class DailySummaryResponse(BaseModel):
    id: int
    date: date
    morning_schedule: Optional[str] = Field(None, json_schema_extra={"example": '{"medicines": ["Metformin"], "appointments": []}'})
    evening_summary: Optional[str] = Field(None, json_schema_extra={"example": '{"systolic_avg": 120.0, "missed_meds": []}'})
    created_at: datetime

    class Config:
        from_attributes = True
