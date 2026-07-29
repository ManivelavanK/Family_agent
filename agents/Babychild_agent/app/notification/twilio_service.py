from twilio.rest import Client
from app.config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER
import logging

logger = logging.getLogger(__name__)

def send_whatsapp_message(to_phone: str, body: str) -> dict:
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        raise ValueError("Twilio credentials are not configured.")
        
    try:
        # Enforce correct Twilio whatsapp: prefixing
        to_addr = to_phone if to_phone.startswith("whatsapp:") else f"whatsapp:{to_phone}"
        from_addr = TWILIO_WHATSAPP_NUMBER if TWILIO_WHATSAPP_NUMBER.startswith("whatsapp:") else f"whatsapp:{TWILIO_WHATSAPP_NUMBER}"
        
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=body,
            from_=from_addr,
            to=to_addr
        )
        logger.info(f"Successfully sent Twilio WhatsApp message SID: {message.sid}")
        return {
            "sid": message.sid,
            "status": message.status
        }
    except Exception as e:
        logger.error(f"Failed to send Twilio WhatsApp message to {to_phone}: {e}")
        raise e
