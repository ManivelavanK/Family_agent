import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_ERROR

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def _job_error_listener(event):
    logger.error("Scheduled job '%s' crashed: %s", event.job_id, event.exception)


def start_scheduler():
    if scheduler.running:
        logger.warning("Scheduler already running — skipping start.")
        return

    scheduler.add_listener(_job_error_listener, EVENT_JOB_ERROR)

    from app.jobs.grocery_job import run_daily_grocery_check
    scheduler.add_job(
        run_daily_grocery_check,
        "interval",
        minutes=60,
        id="daily_grocery_check",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started.")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped.")
