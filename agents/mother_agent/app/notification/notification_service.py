import logging
from sqlalchemy.orm import Session
from app.notification.whatsapp_service import send_message
from app.notification.templates import KITCHEN_ALERT_TEMPLATE
from app.models.settings import HouseholdSettings

logger = logging.getLogger(__name__)


def send_kitchen_alert_notification(db: Session, title: str, severity: str, description: str, action: str) -> dict:
    settings = db.query(HouseholdSettings).first()
    recipient = settings.primary_contact_phone if settings else None

    formatted_text = KITCHEN_ALERT_TEMPLATE.format(
        title=title,
        severity=severity,
        description=description,
        action=action
    )

    logger.info("Dispatching alert notification: %s", title)
    return send_message(recipient, formatted_text)
