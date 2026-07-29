from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.planning_service import generate_weekly_plan

router = APIRouter(prefix="/api/v1/planning", tags=["Planning Agent"])


@router.get("/weekly")
def weekly_plan(db: Session = Depends(get_db)):
    return generate_weekly_plan(db)
