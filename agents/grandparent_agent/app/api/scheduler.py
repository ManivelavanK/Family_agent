import logging
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json

from app.database.database import get_db
from app.scheduler.scheduler import scheduler
from app.models.daily_summary import DailySummary
from app.schemas.response import APIResponse
from app.schemas.daily_summary import DailySummaryResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/scheduler", tags=["Scheduler Control"])


@router.get("/jobs", response_model=APIResponse)
def list_scheduler_jobs():
    """
    Lists all registered background jobs in APScheduler, detailing their triggers and schedules.
    """
    logger.info("Request received: List active scheduler jobs")
    jobs = scheduler.get_jobs()
    job_details = []
    for job in jobs:
        job_details.append({
            "id": job.id,
            "name": job.name,
            "next_run_time": str(job.next_run_time) if job.next_run_time else "Paused/None",
            "trigger": str(job.trigger)
        })
    return APIResponse(
        success=True,
        message="Active scheduler jobs list retrieved",
        data=job_details
    )


@router.post("/run", response_model=APIResponse)
def run_job_manually(job_id: str):
    """
    Triggers a background job immediately by executing its target function.
    """
    logger.info("Request received: Trigger scheduler job manually: %s", job_id)
    job = scheduler.get_job(job_id)
    if not job:
        logger.warning("Scheduler Job manual run failed: Job ID %s not found", job_id)
        return APIResponse(
            success=False,
            message=f"Job ID '{job_id}' not found."
        )

    try:
        # Run job target function synchronously for immediate feedback
        job.func()
        logger.info("Scheduler Job %s executed successfully manually", job_id)
        return APIResponse(
            success=True,
            message=f"Job '{job_id}' executed successfully."
        )
    except Exception as e:
        logger.exception("Failed to execute job %s manually", job_id)
        return APIResponse(
            success=False,
            message=f"Failed to run job manually: {str(e)}"
        )


@router.get("/summary/today", response_model=APIResponse)
def get_today_summary(db: Session = Depends(get_db)):
    """
    Fetches the morning schedule and evening summary generated for today.
    """
    logger.info("Request received: Read today's health daily summary log")
    today = date.today()
    summary = db.query(DailySummary).filter(DailySummary.date == today).first()
    if not summary:
        logger.info("No daily summaries found in database for date: %s", today)
        return APIResponse(
            success=False,
            message="No summary generated for today yet."
        )
    
    # Parse stored JSON structures into dictionary objects to return clean JSON
    morning_dict = json.loads(summary.morning_schedule) if summary.morning_schedule else None
    evening_dict = json.loads(summary.evening_summary) if summary.evening_summary else None

    data = {
        "id": summary.id,
        "date": str(summary.date),
        "morning_schedule": morning_dict,
        "evening_summary": evening_dict,
        "created_at": summary.created_at.isoformat()
    }

    return APIResponse(
        success=True,
        message="Today's schedule and summary retrieved successfully",
        data=data
    )
