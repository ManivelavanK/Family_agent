from pydantic import BaseModel, Field
from typing import Optional, Union


class VitalsSummary(BaseModel):
    avg_systolic: Optional[Union[float, str]] = Field(None, json_schema_extra={"example": 120.0})
    avg_diastolic: Optional[Union[float, str]] = Field(None, json_schema_extra={"example": 80.0})
    avg_heart_rate: Optional[Union[float, str]] = Field(None, json_schema_extra={"example": 72.0})
    avg_blood_sugar: Optional[Union[float, str]] = Field(None, json_schema_extra={"example": 95.5})


class ActivitySummary(BaseModel):
    total_steps: Union[int, str] = Field(0, json_schema_extra={"example": 6000})
    avg_sleep_hours: Union[float, str] = Field(0.0, json_schema_extra={"example": 7.5})
    total_active_minutes: Union[int, str] = Field(0, json_schema_extra={"example": 30})


class AnalyticsSummaryResponse(BaseModel):
    vitals: Union[VitalsSummary, str] = Field(..., json_schema_extra={"example": "No vitals data"})
    activity: Union[ActivitySummary, str] = Field(..., json_schema_extra={"example": "No activity data"})
    nutrition_calories: Union[float, str] = Field(0.0, json_schema_extra={"example": 2000.0})
    water_intake_ml: Union[int, str] = Field(0, json_schema_extra={"example": 1500})
