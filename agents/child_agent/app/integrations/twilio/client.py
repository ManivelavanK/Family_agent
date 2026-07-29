import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

MOCK_SENT_MESSAGES = []


class TwilioWhatsAppClient:
    """
    Twilio WhatsApp API Client.
    Supports real Twilio API calls and test mode via MOCK_TWILIO=true environment variable.
    """

    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.whatsapp_from = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
        self.mock_mode = os.getenv("MOCK_TWILIO", "true").lower() in ("true", "1", "yes")

    def send_whatsapp_message(self, to_phone: str, body: str) -> Dict[str, Any]:
        formatted_to = to_phone if to_phone.startswith("whatsapp:") else f"whatsapp:{to_phone}"

        if self.mock_mode or not self.account_sid or not self.auth_token:
            logger.info(f"[MOCK TWILIO WHATSAPP] To: {formatted_to} | From: {self.whatsapp_from}\n{body}")
            mock_record = {
                "sid": f"SMmock_{len(MOCK_SENT_MESSAGES) + 1}",
                "to": formatted_to,
                "from": self.whatsapp_from,
                "body": body,
                "status": "sent",
                "mock": True,
            }
            MOCK_SENT_MESSAGES.append(mock_record)
            return mock_record

        # Real Twilio API integration using twilio SDK or requests fallback
        try:
            from twilio.rest import Client
            client = Client(self.account_sid, self.auth_token)
            message = client.messages.create(
                from_=self.whatsapp_from,
                body=body,
                to=formatted_to,
            )
            return {
                "sid": message.sid,
                "to": formatted_to,
                "from": self.whatsapp_from,
                "body": body,
                "status": message.status,
                "mock": False,
            }
        except Exception as e:
            logger.error(f"Failed to dispatch Twilio WhatsApp message: {e}")
            return {
                "sid": None,
                "error": str(e),
                "status": "failed",
                "mock": False,
            }
