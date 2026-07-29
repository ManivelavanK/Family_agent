from pydantic import BaseModel, Field
from typing import Dict, Any


class WhatsAppSendRequest(BaseModel):
    phone: str = Field(..., json_schema_extra={"example": "+919999999999"})
    type: str = Field(..., json_schema_extra={"example": "medicine"})  # medicine, emergency, low_stock, etc.
    variables: Dict[str, Any] = Field(
        ..., 
        json_schema_extra={
            "example": {
                "name": "Lakshmi",
                "medicine": "Metformin",
                "time": "8:00 PM"
            }
        }
    )


class WhatsAppTestRequest(BaseModel):
    phone: str = Field(..., json_schema_extra={"example": "+919999999999"})


class AgentNotificationRequest(BaseModel):
    source_agent: str = Field(..., json_schema_extra={"example": "Mother"})
    event: str = Field(..., json_schema_extra={"example": "Low Grocery"})
    message: str = Field(..., json_schema_extra={"example": "Milk will finish tomorrow."})
