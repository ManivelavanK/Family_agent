from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class WhatsAppTestNotificationRequest(BaseModel):
    child_id: int = Field(..., description="Target Child ID e.g. 1")
    message_type: str = Field("HOMEWORK_REMINDER", description="HOMEWORK_REMINDER, HOMEWORK_OVERDUE, EXAM_APPROACHING, SAFETY_ALERT")
    template_data: Optional[Dict[str, Any]] = Field(None, description="Optional payload overrides for template data")


class WhatsAppTestNotificationResponse(BaseModel):
    success: bool
    message_sid: Optional[str] = None
    channel: str = "whatsapp"
    notification_type: str
    status: str
    error: Optional[str] = None

