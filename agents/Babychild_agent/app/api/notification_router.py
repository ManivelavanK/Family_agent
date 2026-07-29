from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, field_validator
import logging

from app.notification import twilio_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])

class TestNotificationRequest(BaseModel):
    phone_number: str
    message: str

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Phone number is required.")
        return v.strip()

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Message is required.")
        return v.strip()

@router.post("/test")
def test_whatsapp_notification(payload: TestNotificationRequest):
    try:
        res = twilio_service.send_whatsapp_message(
            to_phone=payload.phone_number,
            body=payload.message
        )
        return {
            "success": True,
            "message": "Test WhatsApp notification sent successfully.",
            "data": res
        }
    except Exception as e:
        logger.error(f"Error sending test WhatsApp notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send test notification: {str(e)}"
        )
