import logging
from app import config

logger = logging.getLogger(__name__)

try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
    HAS_TWILIO = True
except ImportError:
    HAS_TWILIO = False
    logger.warning("Twilio module not found. WhatsApp Service will run in mock-only mode.")


def check_service_mode() -> str:
    """
    Validates configuration at startup and prints execution status mode.
    Called during FastAPI lifespan startup.
    """
    if not HAS_TWILIO:
        print("WhatsApp Service running in MOCK mode")
        return "MOCK"
    if not config.TWILIO_ACCOUNT_SID or not config.TWILIO_AUTH_TOKEN or not config.TWILIO_WHATSAPP_NUMBER:
        print("WhatsApp Service running in MOCK mode")
        return "MOCK"
    print("WhatsApp Service running in REAL mode")
    return "REAL"


def validate_phone(phone: str) -> bool:
    """
    Validates if a phone number matches Twilio requirements (starts with + and contains enough digits).
    """
    if not phone:
        return False
    clean = phone.replace("whatsapp:", "").strip()
    return clean.startswith("+") and len(clean) >= 8


def format_phone(phone: str) -> str:
    """
    Ensures the phone number is prefixed with 'whatsapp:' as required by Twilio WhatsApp API.
    """
    phone = phone.strip()
    if not phone.startswith("whatsapp:"):
        return f"whatsapp:{phone}"
    return phone


def send_message(phone: str, text: str) -> dict:
    """
    Dispatches a WhatsApp message using the Twilio client.
    Automatically falls back to Mock Mode if credentials are not configured.
    """
    target_recipient = phone if phone else config.DEFAULT_FAMILY_PHONE
    to_phone = format_phone(target_recipient)

    logger.info("Sending WhatsApp message...")
    logger.info("Recipient : %s", to_phone)

    # 1. Validation check when trying to send
    is_configured = config.TWILIO_ACCOUNT_SID and config.TWILIO_AUTH_TOKEN and config.TWILIO_WHATSAPP_NUMBER
    
    # If partial configurations exist, return a descriptive error
    if (config.TWILIO_ACCOUNT_SID or config.TWILIO_AUTH_TOKEN or config.TWILIO_WHATSAPP_NUMBER) and not is_configured:
        missing = []
        if not config.TWILIO_ACCOUNT_SID:
            missing.append("TWILIO_ACCOUNT_SID")
        if not config.TWILIO_AUTH_TOKEN:
            missing.append("TWILIO_AUTH_TOKEN")
        if not config.TWILIO_WHATSAPP_NUMBER:
            missing.append("TWILIO_WHATSAPP_NUMBER")
        err_msg = f"Configuration error: Missing variables: {', '.join(missing)}"
        logger.error(err_msg)
        return {
            "status": "Failed",
            "reason": err_msg
        }

    # 2. Mock Fallback
    if not HAS_TWILIO or not is_configured:
        logger.warning("WhatsApp Service: Twilio credentials not set or package missing. Simulating mock delivery.")
        logger.info("Message SID : mock_sid_123456789")
        logger.info("Delivery successful (Mock)")
        return {
            "status": "Mock Delivered",
            "sid": "mock_sid_123456789",
            "recipient": to_phone,
            "body": text
        }

    # 3. Real Dispatch
    try:
        # Validate recipient phone format first
        if not validate_phone(to_phone):
            logger.error("Invalid phone format: %s", to_phone)
            return {
                "status": "Failed",
                "reason": f"Invalid phone format: '{to_phone}'. Must start with '+' followed by country code and digits."
            }

        client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            from_=config.TWILIO_WHATSAPP_NUMBER,
            body=text,
            to=to_phone
        )
        
        logger.info("Message SID : %s", message.sid)
        logger.info("Delivery successful")
        return {
            "status": "Delivered",
            "sid": message.sid,
            "recipient": to_phone,
            "body": text
        }
    except TwilioRestException as e:
        error_explanation = f"Twilio API error {e.code}: {e.msg}"
        if e.code == 21608:
            error_explanation = "Twilio Sandbox Error: The recipient has not joined the Twilio WhatsApp Sandbox yet. Ask them to send the sandbox join keyword."
        elif e.code == 20003:
            error_explanation = "Authentication failure: Invalid Twilio SID or Auth Token."
        elif e.code == 21211:
            error_explanation = "Invalid number: Twilio reports the phone number is invalid."
        elif e.code == 20429:
            error_explanation = "Rate limit exceeded: Twilio rate limits hit."
            
        logger.error("WhatsApp Service: %s", error_explanation)
        return {
            "status": "Failed",
            "error_code": e.code,
            "reason": error_explanation,
            "recipient": to_phone
        }
    except Exception as e:
        logger.exception("WhatsApp Service: Network connection or timeout error")
        return {
            "status": "Failed",
            "reason": f"Connection/Timeout failure: {str(e)}",
            "recipient": to_phone
        }


def send_bulk_message(list_of_numbers: list[str], text: str) -> list[dict]:
    """
    Dispatches a single message template in bulk to a list of phone numbers.
    """
    logger.info("WhatsApp Service: Sending bulk message to %d numbers", len(list_of_numbers))
    results = []
    for num in list_of_numbers:
        results.append(send_message(num, text))
    return results
