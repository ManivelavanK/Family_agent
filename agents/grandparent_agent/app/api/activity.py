import logging
from datetime import date
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.activity import Activity
from app.schemas.activity import ActivityCreate, ActivityResponse
from app.schemas.response import APIResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/activity", tags=["Activity"])


@router.post("/add", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def create_activity_log(act_in: ActivityCreate, db: Session = Depends(get_db)):
    logger.info("Request received: Add/Update activity log")
    existing = db.query(Activity).filter(Activity.date == act_in.date).first()
    if existing:
        existing.steps += act_in.steps
        existing.sleep_hours += act_in.sleep_hours
        existing.duration_minutes += act_in.duration_minutes
        if act_in.activity_type:
            existing.activity_type = act_in.activity_type
        db_act = existing
    else:
        db_act = Activity(
            date=act_in.date,
            steps=act_in.steps,
            sleep_hours=act_in.sleep_hours,
            activity_type=act_in.activity_type,
            duration_minutes=act_in.duration_minutes
        )
        db.add(db_act)
    db.commit()
    db.refresh(db_act)
    logger.info("Database updated: Activity logged successfully")
    return APIResponse(
        success=True,
        message="Activity logged successfully",
        data=ActivityResponse.model_validate(db_act)
    )


@router.get("/", response_model=APIResponse)
def list_activities(limit: int = 30, db: Session = Depends(get_db)):
    logger.info("Request received: List activity logs")
    logs = db.query(Activity).order_by(Activity.date.desc()).limit(limit).all()
    data = [ActivityResponse.model_validate(log) for log in logs]
    return APIResponse(
        success=True,
        message="Activities retrieved successfully",
        data=data
    )


@router.put("/{act_id}", response_model=APIResponse)
def modify_activity(act_id: int, act_in: ActivityCreate, db: Session = Depends(get_db)):
    logger.info("Request received: Update activity ID %d", act_id)
    existing = db.query(Activity).filter(Activity.id == act_id).first()
    if not existing:
        logger.warning("Activity update failed: Activity ID not found")
        return APIResponse(
            success=False,
            message="Activity not found"
        )
    existing.date = act_in.date
    existing.steps = act_in.steps
    existing.sleep_hours = act_in.sleep_hours
    existing.activity_type = act_in.activity_type
    existing.duration_minutes = act_in.duration_minutes
    db.commit()
    db.refresh(existing)
    logger.info("Database updated: Activity ID %d updated", act_id)
    return APIResponse(
        success=True,
        message="Activity updated successfully",
        data=ActivityResponse.model_validate(existing)
    )


@router.delete("/{act_id}", response_model=APIResponse)
def remove_activity(act_id: int, db: Session = Depends(get_db)):
    logger.info("Request received: Delete activity ID %d", act_id)
    existing = db.query(Activity).filter(Activity.id == act_id).first()
    if not existing:
        logger.warning("Activity deletion failed: Activity not found")
        return APIResponse(
            success=False,
            message="Activity not found"
        )
    db.delete(existing)
    db.commit()
    logger.info("Database updated: Activity ID %d deleted", act_id)
    return APIResponse(
        success=True,
        message="Activity deleted successfully"
    )
