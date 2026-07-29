from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.nutrition import (
    NutritionLogCreate,
    NutritionLogResponse,
    NutritionSummaryResponse,
    MotherAgentBridgeEventCreate,
    MotherAgentBridgeEventResponse,
)
from app.services import nutrition_service

router = APIRouter(tags=["Nutrition & Hydration Agent"])


# --- Nutrition Log APIs ---

@router.post("/children/nutrition/log", response_model=NutritionLogResponse, status_code=status.HTTP_201_CREATED)
def record_nutrition_log(log: NutritionLogCreate, db: Session = Depends(get_db)):
    return nutrition_service.create_or_update_nutrition_log(db=db, log_in=log)


@router.get("/children/nutrition/{child_id}/log", response_model=Optional[NutritionLogResponse])
def get_nutrition_log_by_date(child_id: int, log_date: Optional[str] = None, db: Session = Depends(get_db)):
    target_date = date.today()
    if log_date:
        try:
            target_date = date.fromisoformat(log_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="log_date must be in YYYY-MM-DD format"
            )
    log = nutrition_service.get_nutrition_log_by_date(db=db, child_id=child_id, log_date=target_date)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No nutrition log found for child ID {child_id} on {target_date}"
        )
    return log


@router.get("/children/nutrition/{child_id}/logs", response_model=List[NutritionLogResponse])
def get_child_nutrition_logs(child_id: int, days: int = Query(14, ge=1, le=60), db: Session = Depends(get_db)):
    return nutrition_service.get_child_nutrition_logs(db=db, child_id=child_id, limit=days)


# --- Analytics, Consistency & Reminders API ---

@router.get("/children/nutrition/{child_id}/summary", response_model=NutritionSummaryResponse)
def get_nutrition_summary(child_id: int, days: int = Query(7, ge=1, le=30), db: Session = Depends(get_db)):
    return nutrition_service.get_nutrition_summary(db=db, child_id=child_id, days=days)


# --- Mother Agent Integration Bridge APIs ---

@router.post("/children/nutrition/mother-agent-event", response_model=MotherAgentBridgeEventResponse, status_code=status.HTTP_201_CREATED)
def create_mother_agent_event(event: MotherAgentBridgeEventCreate, db: Session = Depends(get_db)):
    return nutrition_service.create_mother_agent_bridge_event(db=db, event_in=event)


@router.get("/children/nutrition/{child_id}/mother-agent-events", response_model=List[MotherAgentBridgeEventResponse])
def get_mother_agent_events(child_id: int, db: Session = Depends(get_db)):
    return nutrition_service.get_mother_agent_bridge_events(db=db, child_id=child_id)
