import logging
import uuid
from datetime import datetime
from app.schemas.reminder import ReminderCreate, ReminderResponse
from app.services.notification_service import send_notification

logger = logging.getLogger(__name__)

# In-memory store for active reminders (persisting across the runtime)
_active_reminders = {}


def add_reminder(reminder: ReminderCreate) -> ReminderResponse:
    from app.scheduler.scheduler import scheduler

    rem_id = str(uuid.uuid4())[:8]

    # Helper function to fire notification
    def fire_reminder_job():
        send_notification(
            title=f"Reminder: {reminder.title}",
            body=f"[{reminder.reminder_type}] {reminder.notes or ''}",
            notification_type="Alert"
        )
        if rem_id in _active_reminders:
            _active_reminders[rem_id]["is_active"] = False

    # Schedule standard one-off alarm job
    scheduler.add_job(
        fire_reminder_job,
        trigger="date",
        run_date=reminder.trigger_time,
        id=f"reminder_{rem_id}"
    )

    response = ReminderResponse(
        id=rem_id,
        title=reminder.title,
        trigger_time=reminder.trigger_time,
        reminder_type=reminder.reminder_type,
        notes=reminder.notes,
        is_active=True
    )
    _active_reminders[rem_id] = response.model_dump()
    logger.info("Scheduled reminder ID %s at %s.", rem_id, reminder.trigger_time)
    return response


def get_reminders(active_only: bool = True) -> list[ReminderResponse]:
    results = []
    for r in _active_reminders.values():
        if not active_only or r["is_active"]:
            results.append(ReminderResponse(**r))
    return results


def update_reminder(rem_id: str, reminder_in: ReminderCreate) -> ReminderResponse:
    from app.scheduler.scheduler import scheduler

    if rem_id not in _active_reminders:
        raise ValueError(f"Reminder with ID {rem_id} not found.")

    # Remove previous scheduled job if exists
    try:
        scheduler.remove_job(f"reminder_{rem_id}")
    except Exception:
        pass

    # Helper function to fire notification
    def fire_reminder_job():
        send_notification(
            title=f"Reminder: {reminder_in.title}",
            body=f"[{reminder_in.reminder_type}] {reminder_in.notes or ''}",
            notification_type="Alert"
        )
        if rem_id in _active_reminders:
            _active_reminders[rem_id]["is_active"] = False

    # Re-schedule with new details
    scheduler.add_job(
        fire_reminder_job,
        trigger="date",
        run_date=reminder_in.trigger_time,
        id=f"reminder_{rem_id}"
    )

    response = ReminderResponse(
        id=rem_id,
        title=reminder_in.title,
        trigger_time=reminder_in.trigger_time,
        reminder_type=reminder_in.reminder_type,
        notes=reminder_in.notes,
        is_active=True
    )
    _active_reminders[rem_id] = response.model_dump()
    logger.info("Rescheduled reminder ID %s at %s.", rem_id, reminder_in.trigger_time)
    return response


def cancel_reminder(rem_id: str):
    from app.scheduler.scheduler import scheduler

    job_id = f"reminder_{rem_id}"
    try:
        scheduler.remove_job(job_id)
    except Exception:
        pass

    if rem_id in _active_reminders:
        _active_reminders[rem_id]["is_active"] = False
        logger.info("Cancelled reminder ID %s.", rem_id)
