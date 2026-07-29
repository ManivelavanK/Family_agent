from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database.database import get_db
from app.schemas.whatsapp_webhook import WhatsAppAssistantResponse
from app.services.two_way_whatsapp_service import TwoWayWhatsAppParentAssistant

router = APIRouter(tags=["Twilio Two-Way WhatsApp Assistant"])


@router.post("/twilio/whatsapp/webhook")
async def twilio_whatsapp_webhook(
    request: Request,
    From: str = Form(...),
    To: str = Form(...),
    Body: str = Form(...),
    MessageSid: Optional[str] = Form(None),
    child_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    Twilio WhatsApp Webhook Endpoint.
    Receives incoming parent WhatsApp messages and processes them through Parent Authentication,
    Family Isolation, Privacy Engine, and AI Supervisor.
    """
    assistant = TwoWayWhatsAppParentAssistant(db=db)

    # Verify signature
    signature = request.headers.get("X-Twilio-Signature")
    url = str(request.url)
    params = dict(await request.form())

    if not assistant.verify_webhook_signature(signature, url, params):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Twilio Webhook Signature")

    res = assistant.process_parent_query(from_phone=From, query_text=Body, requested_child_id=child_id)
    return {
        "status": res["status"],
        "reply": res.get("reply"),
    }
