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

    # Hourly checks
    from app.scheduler.jobs import (
        run_daily_refill_check,
        run_hourly_health_rules_check,
        run_hourly_appointment_check,
        run_morning_schedule_generation,
        run_evening_summary_generation,
        run_weekly_report_generation,
        run_emergency_escalation_check
    )

    scheduler.add_job(
        run_daily_refill_check,
        "interval",
        minutes=60,
        id="daily_refill_check",
        replace_existing=True,
    )

    scheduler.add_job(
        run_hourly_health_rules_check,
        "interval",
        minutes=60,
        id="hourly_health_rules_check",
        replace_existing=True,
    )

    scheduler.add_job(
        run_hourly_appointment_check,
        "interval",
        minutes=60,
        id="hourly_appointment_check",
        replace_existing=True,
    )

    # Cron tasks: Morning (8 AM) and Evening (8 PM)
    scheduler.add_job(
        run_morning_schedule_generation,
        "cron",
        hour=8,
        minute=0,
        id="morning_schedule_generation",
        replace_existing=True,
    )

    scheduler.add_job(
        run_evening_summary_generation,
        "cron",
        hour=20,
        minute=0,
        id="evening_summary_generation",
        replace_existing=True,
    )

    # Weekly report generation (Sundays at 11 PM)
    scheduler.add_job(
        run_weekly_report_generation,
        "cron",
        day_of_week="sun",
        hour=23,
        minute=0,
        id="weekly_report_generation",
        replace_existing=True,
    )

    # Emergency escalation check (every 5 minutes)
    scheduler.add_job(
        run_emergency_escalation_check,
        "interval",
        minutes=5,
        id="emergency_escalation_check",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started with hourly, morning (8 AM), and evening (7 PM) monitoring jobs.")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped.")
