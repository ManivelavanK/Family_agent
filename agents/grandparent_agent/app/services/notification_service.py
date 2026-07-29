import logging

logger = logging.getLogger(__name__)


def send_notification(title: str, body: str, notification_type: str = "Info"):
    """
    Mock sending a notification (prints to stdout/logs).
    In a real system, this would trigger Push notifications, SMS or Emails.
    """
    logger.info(f"[{notification_type.upper()}] Notification Sent: '{title}' - {body}")
    print(f"[{notification_type.upper()}] Notification Sent: '{title}' - {body}")
