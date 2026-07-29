import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class TwilioWhatsAppService:
    """
    STEP 2: Dedicated Real Twilio WhatsApp Service.
    Initializes directly from environment variables. Never exposes credentials.
    """

    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.whatsapp_from = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")

        if not self.account_sid or not self.auth_token or self.account_sid.startswith("your_"):
            logger.warning("Twilio credentials not configured in environment or using placeholder values.")

    def send_whatsapp_message(self, to_phone: str, body: str) -> Dict[str, Any]:
        """
        Dispatches message via real Twilio API.
        Returns dict containing 'sid', 'status', 'to', 'from'.
        Never exposes TWILIO_AUTH_TOKEN in output or exceptions.
        """
        formatted_to = to_phone if to_phone.startswith("whatsapp:") else f"whatsapp:{to_phone}"
        formatted_from = self.whatsapp_from if self.whatsapp_from.startswith("whatsapp:") else f"whatsapp:{self.whatsapp_from}"

        if not self.account_sid or not self.auth_token or self.account_sid.startswith("your_"):
            error_msg = "REAL TWILIO INTEGRATION REQUIRED: Valid TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set in .env"
            logger.warning(error_msg)
            return {
                "sid": None,
                "to": formatted_to,
                "from": formatted_from,
                "status": "failed",
                "error": error_msg,
            }


        logger.info(f"Sending Real Twilio WhatsApp message to {formatted_to}")

        try:
            from twilio.rest import Client
            client = Client(self.account_sid, self.auth_token)
            message = client.messages.create(
                from_=formatted_from,
                body=body,
                to=formatted_to,
            )
            logger.info(f"Twilio WhatsApp message sent successfully. SID: {message.sid}, Status: {message.status}")
            return {
                "sid": message.sid,
                "to": formatted_to,
                "from": formatted_from,
                "status": message.status,
                "error": None,
            }
        except Exception as e:
            # Mask credentials if present in exception string
            error_msg = str(e)
            if self.auth_token and self.auth_token in error_msg:
                error_msg = error_msg.replace(self.auth_token, "********")
            logger.error(f"Twilio API Error sending WhatsApp message: {error_msg}")
            return {
                "sid": None,
                "to": formatted_to,
                "from": formatted_from,
                "status": "failed",
                "error": error_msg,
            }
