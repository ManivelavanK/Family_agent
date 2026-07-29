from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.waste_service import analyze_waste

router = APIRouter(prefix="/api/v1/waste", tags=["Waste Prevention Agent"])


@router.get("/analyze")
def waste_analysis(db: Session = Depends(get_db)):
    return analyze_waste(db)
