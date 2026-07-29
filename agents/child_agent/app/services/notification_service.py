import logging
from typing import List, Optional
from enum import Enum
from sqlalchemy.orm import Session
from app.models.notification import NotificationLog
from app.models.profile import ChildProfile

logger = logging.getLogger(__name__)


class NotificationChannel(str, Enum):
    IN_APP = "IN_APP"
    EMAIL = "EMAIL"
    WHATSAPP = "WHATSAPP"
    TELEGRAM = "TELEGRAM"
    PUSH = "PUSH"


class NotificationType(str, Enum):
    HOMEWORK_REMINDER = "HOMEWORK_REMINDER"
    EXAM_REMINDER = "EXAM_REMINDER"
    ACTIVITY_REMINDER = "ACTIVITY_REMINDER"
    WATER_REMINDER = "WATER_REMINDER"
    SLEEP_REMINDER = "SLEEP_REMINDER"
    ATTENDANCE_WARNING = "ATTENDANCE_WARNING"
    SAFETY_WARNING = "SAFETY_WARNING"
    POCKET_MONEY_REMINDER = "POCKET_MONEY_REMINDER"
    STUDY_REMINDER = "STUDY_REMINDER"


class NotificationService:
    """
    Notification service abstraction supporting multiple delivery channels:
    IN_APP, EMAIL, WHATSAPP, TELEGRAM, PUSH.
    Currently logs notifications safely to logger and persists them to the notification_logs table.
    """

    @staticmethod
    def send_notification(
        db: Session,
        child_id: int,
        title: str,
        message: str,
        notification_type: str,
        channel: str = "IN_APP",
    ) -> NotificationLog:
        # Validate child existence
        child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
        child_name = child.name if child else f"Child #{child_id}"

        # Safe logging of the notification abstraction
        logger.info(
            f"[NOTIFICATION - {channel.upper()}] [{notification_type}] For {child_name} (ID: {child_id}): {title} - {message}"
        )

        # Dispatcher placeholder for future direct integrations (WhatsApp, Email, Telegram, Push)
        if channel.upper() == NotificationChannel.WHATSAPP.value:
            # Future WhatsApp API dispatch logic (Twilio / Meta Graph API)
            pass
        elif channel.upper() == NotificationChannel.EMAIL.value:
            # Future Email dispatch logic (SMTP / SendGrid)
            pass
        elif channel.upper() == NotificationChannel.TELEGRAM.value:
            # Future Telegram bot dispatch logic
            pass
        elif channel.upper() == NotificationChannel.PUSH.value:
            # Future Push notification logic (Firebase FCM)
            pass

        # Persist notification log
        log_entry = NotificationLog(
            child_id=child_id,
            title=title,
            message=message,
            notification_type=notification_type,
            channel=channel.upper(),
            status="LOGGED",
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry

    @staticmethod
    def get_notifications_for_child(
        db: Session, child_id: int, limit: int = 50
    ) -> List[NotificationLog]:
        return (
            db.query(NotificationLog)
            .filter(NotificationLog.child_id == child_id)
            .order_by(NotificationLog.created_at.desc())
            .limit(limit)
            .all()
        )
