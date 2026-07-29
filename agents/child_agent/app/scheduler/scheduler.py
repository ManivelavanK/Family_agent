import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.scheduler import jobs

logger = logging.getLogger(__name__)

# Single BackgroundScheduler instance
scheduler = BackgroundScheduler(daemon=True)
_is_started = False


def register_scheduler_jobs(sched: BackgroundScheduler):
    """Registers all 9 required background jobs to the APScheduler instance."""
    # Homework reminder - every 12 hours
    sched.add_job(
        jobs.check_homework_reminders,
        trigger=IntervalTrigger(hours=12),
        id="homework_reminder_job",
        replace_existing=True,
    )
    # Exam reminder - every 12 hours
    sched.add_job(
        jobs.check_exam_reminders,
        trigger=IntervalTrigger(hours=12),
        id="exam_reminder_job",
        replace_existing=True,
    )
    # Activity reminder - every 6 hours
    sched.add_job(
        jobs.check_activity_reminders,
        trigger=IntervalTrigger(hours=6),
        id="activity_reminder_job",
        replace_existing=True,
    )
    # Water reminder - every 4 hours
    sched.add_job(
        jobs.check_water_reminders,
        trigger=IntervalTrigger(hours=4),
        id="water_reminder_job",
        replace_existing=True,
    )
    # Sleep reminder - every 24 hours
    sched.add_job(
        jobs.check_sleep_reminders,
        trigger=IntervalTrigger(hours=24),
        id="sleep_reminder_job",
        replace_existing=True,
    )
    # Attendance warning - every 24 hours
    sched.add_job(
        jobs.check_attendance_warnings,
        trigger=IntervalTrigger(hours=24),
        id="attendance_warning_job",
        replace_existing=True,
    )
    # Safety check-in warning - every 2 hours
    sched.add_job(
        jobs.check_safety_checkin_warnings,
        trigger=IntervalTrigger(hours=2),
        id="safety_warning_job",
        replace_existing=True,
    )
    # Pocket-money reminder - every 24 hours
    sched.add_job(
        jobs.check_pocket_money_reminders,
        trigger=IntervalTrigger(hours=24),
        id="pocket_money_reminder_job",
        replace_existing=True,
    )
    # Study reminder - every 12 hours
    sched.add_job(
        jobs.check_study_reminders,
        trigger=IntervalTrigger(hours=12),
        id="study_reminder_job",
        replace_existing=True,
    )


def start_scheduler():
    """Starts the background scheduler safely."""
    global _is_started
    if not scheduler.running and not _is_started:
        try:
            register_scheduler_jobs(scheduler)
            scheduler.start()
            _is_started = True
            logger.info("APScheduler background scheduler started successfully with 9 jobs.")
        except Exception as e:
            logger.error(f"Failed to start APScheduler: {e}", exc_info=True)
    else:
        logger.info("APScheduler background scheduler is already running.")


def shutdown_scheduler():
    """Shuts down the background scheduler safely."""
    global _is_started
    if scheduler.running:
        try:
            scheduler.shutdown(wait=False)
            _is_started = False
            logger.info("APScheduler background scheduler shut down successfully.")
        except Exception as e:
            logger.error(f"Failed to shut down APScheduler: {e}", exc_info=True)
    else:
        logger.info("APScheduler background scheduler is not running.")
