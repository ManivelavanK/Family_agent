from pydantic import BaseModel, Field


class AgentEventPayload(BaseModel):
    event: str = Field(..., json_schema_extra={"example": "High Blood Pressure"})
    severity: str = Field(..., json_schema_extra={"example": "High"})
    message: str = Field(..., json_schema_extra={"example": "Grandparent requires medical attention."})
