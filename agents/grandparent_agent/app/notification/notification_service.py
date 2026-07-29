import logging
from sqlalchemy.orm import Session
from app.notification.templates import render_template
from app.notification.whatsapp_service import send_message, send_bulk_message
from app.models.profile import Profile
from app import config

logger = logging.getLogger(__name__)


def notify_medicine(phone: str, name: str, medicine: str, time: str) -> dict:
    """Sends a medicine intake reminder."""
    variables = {"name": name, "medicine": medicine, "time": time}
    text = render_template("medicine", variables)
    return send_message(phone, text)


def notify_emergency(db: Session, reason: str, severity: str, notes: str) -> list[dict]:
    """
    Critical emergency escalations: Sends alerts in bulk to configured family
    contacts (Son, Daughter, Caregiver) retrieved from Profile or config fallbacks.
    """
    logger.info("Notification Service: Dispatching critical emergency alert...")
    
    # Compile contact list
    recipients = []
    profile = db.query(Profile).first() if db else None
    
    if profile and profile.emergency_contact_phone:
        recipients.append(profile.emergency_contact_phone)
        
    # Append fallback default family phone to ensure delivery
    if config.DEFAULT_FAMILY_PHONE not in recipients:
        recipients.append(config.DEFAULT_FAMILY_PHONE)

    variables = {
        "reason": reason,
        "severity": severity,
        "notes": notes or "No extra notes provided."
    }
    text = render_template("emergency", variables)
    return send_bulk_message(recipients, text)


def notify_low_stock(phone: str, medicine: str, count: int) -> dict:
    """Sends a low-inventory warning."""
    variables = {"medicine": medicine, "count": str(count)}
    text = render_template("low_stock", variables)
    return send_message(phone, text)


def notify_appointment(phone: str, doctor: str, specialty: str, time: str) -> dict:
    """Sends a doctor appointment reminder."""
    variables = {"doctor": doctor, "specialty": specialty, "time": time}
    text = render_template("appointment", variables)
    return send_message(phone, text)


def notify_health_summary(phone: str, bp: str, sleep: float, water: float, status: str) -> dict:
    """Sends daily wellness summary."""
    variables = {
        "bp": bp,
        "sleep": f"{sleep:.1f}" if isinstance(sleep, float) else str(sleep),
        "water": f"{water:.0f}" if isinstance(water, float) else str(water),
        "status": status
    }
    text = render_template("daily_summary", variables)
    return send_message(phone, text)


def notify_custom_message(phone: str, message: str) -> dict:
    """Sends a general custom WhatsApp notification."""
    text = render_template("custom", {"message": message})
    return send_message(phone, text)
