import logging
from fastapi import APIRouter, status
from app.schemas.reminder import ReminderCreate, ReminderResponse
from app.schemas.response import APIResponse
from app.services.reminder_service import add_reminder, get_reminders, update_reminder, cancel_reminder

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/reminder", tags=["Reminder"])


@router.post("/add", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def create_reminder(reminder_in: ReminderCreate):
    logger.info("Request received: Add scheduled reminder")
    rem = add_reminder(reminder_in)
    logger.info("Scheduler triggered: Reminder ID %s created", rem.id)
    return APIResponse(
        success=True,
        message="Reminder scheduled successfully",
        data=rem
    )


@router.get("/", response_model=APIResponse)
def list_reminders(active_only: bool = True):
    logger.info("Request received: List scheduled reminders")
    reminders = get_reminders(active_only)
    return APIResponse(
        success=True,
        message="Reminders retrieved successfully",
        data=reminders
    )


@router.put("/{rem_id}", response_model=APIResponse)
def modify_reminder(rem_id: str, reminder_in: ReminderCreate):
    logger.info("Request received: Update reminder ID %s", rem_id)
    try:
        rem = update_reminder(rem_id, reminder_in)
        logger.info("Scheduler triggered: Reminder ID %s updated", rem_id)
        return APIResponse(
            success=True,
            message="Reminder updated successfully",
            data=rem
        )
    except ValueError as e:
        logger.warning("Reminder update failed: %s", str(e))
        return APIResponse(
            success=False,
            message=str(e)
        )


@router.delete("/{rem_id}", response_model=APIResponse)
def remove_reminder(rem_id: str):
    logger.info("Request received: Delete/Cancel reminder ID %s", rem_id)
    cancel_reminder(rem_id)
    logger.info("Scheduler triggered: Reminder ID %s cancelled", rem_id)
    return APIResponse(
        success=True,
        message="Reminder cancelled successfully"
    )
