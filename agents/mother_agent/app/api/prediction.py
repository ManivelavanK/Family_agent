from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.prediction_service import predict_consumption

router = APIRouter(prefix="/api/v1/prediction", tags=["Prediction Agent"])


@router.get("/{item_name}")
def prediction(item_name: str, db: Session = Depends(get_db)):
    result = predict_consumption(db, item_name)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=result["error"])
    return result
