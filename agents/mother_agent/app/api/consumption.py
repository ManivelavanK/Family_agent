from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.consumption import ConsumptionCreate, ConsumptionResponse
from app.services.consumption_service import add_consumption, get_consumption_history

router = APIRouter(prefix="/api/v1/consumption", tags=["Consumption"])


@router.post("/add", response_model=ConsumptionResponse, status_code=status.HTTP_201_CREATED)
def create_consumption(consumption: ConsumptionCreate, db: Session = Depends(get_db)):
    return add_consumption(db, consumption)


@router.get("/history", response_model=list[ConsumptionResponse])
def history(db: Session = Depends(get_db)):
    return get_consumption_history(db)
