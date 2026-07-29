from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class SOSRequest(BaseModel):
    reason: Optional[str] = Field("Manual emergency button pressed", max_length=200, json_schema_extra={"example": "Slipped in restroom"})
    severity: Optional[str] = Field("Critical", max_length=50, json_schema_extra={"example": "Critical"})
    notes: Optional[str] = Field(None, json_schema_extra={"example": "Found on floor, conscious but in pain."})


class EmergencyIncidentResponse(BaseModel):
    id: int = Field(..., json_schema_extra={"example": 1})
    time: datetime = Field(..., json_schema_extra={"example": "2026-07-28T12:00:00"})
    reason: str = Field(..., json_schema_extra={"example": "Slipped in restroom"})
    severity: str = Field(..., json_schema_extra={"example": "Critical"})
    status: str = Field(..., json_schema_extra={"example": "Active"})
    family_notified: bool = Field(..., json_schema_extra={"example": True})
    notes: Optional[str] = Field(None, json_schema_extra={"example": "Found on floor"})

    class Config:
        from_attributes = True
