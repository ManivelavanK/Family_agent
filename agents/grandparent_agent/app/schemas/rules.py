from pydantic import BaseModel, Field


class AlertItem(BaseModel):
    severity: str = Field(..., json_schema_extra={"example": "High"})
    title: str = Field(..., json_schema_extra={"example": "High Blood Pressure"})
    description: str = Field(..., json_schema_extra={"example": "Blood pressure is above the recommended level."})
    recommended_action: str = Field(..., json_schema_extra={"example": "Consult your physician."})
