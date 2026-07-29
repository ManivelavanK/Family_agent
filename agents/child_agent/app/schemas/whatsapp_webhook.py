from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class WhatsAppWebhookPayload(BaseModel):
    From: str = Field(..., description="Sender phone number e.g. whatsapp:+15550199")
    To: str = Field(..., description="Recipient phone number e.g. whatsapp:+14155238886")
    Body: str = Field(..., description="Incoming message text")
    MessageSid: Optional[str] = Field(None, description="Twilio message SID")
    AccountSid: Optional[str] = Field(None, description="Twilio account SID")


class WhatsAppAssistantResponse(BaseModel):
    status: str
    parent_phone: str
    reply_body: str
    child_id: Optional[int] = None
    family_id: Optional[str] = None
