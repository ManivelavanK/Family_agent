from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.analysis import AnalysisResponse
from app.services.analyzer_service import analyze_item

router = APIRouter(prefix="/api/v1/analysis", tags=["Consumption Analysis"])


@router.get("/{item_name}", response_model=AnalysisResponse)
def analyze(item_name: str, db: Session = Depends(get_db)):
    result = analyze_item(db, item_name)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item '{item_name}' not found in inventory.",
        )
    return result
