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

    from app.scheduler.jobs import check_baby_alerts_job, vaccination_reminders_job, daily_summaries_job
    
    scheduler.add_job(check_baby_alerts_job, "interval", hours=1, id="check_baby_alerts", replace_existing=True)
    scheduler.add_job(vaccination_reminders_job, "cron", hour=9, minute=0, id="vaccination_reminders", replace_existing=True)
    scheduler.add_job(daily_summaries_job, "cron", hour=20, minute=0, id="daily_summaries", replace_existing=True)

    scheduler.start()
    logger.info("Scheduler started.")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped.")
