from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.prediction import PredictionResponse, MLTrainResponse
from app.ml import predictor, train

router = APIRouter(tags=["Children Agent ML Predictions"])


@router.post("/children/ml/train", response_model=MLTrainResponse, status_code=status.HTTP_200_OK)
def train_ml_models(db: Session = Depends(get_db)):
    """Triggers Scikit-learn model training across all database domains and persists model binaries."""
    return train.train_all_models(db=db)


@router.get("/children/predict/homework/{child_id}", response_model=PredictionResponse)
def predict_homework_completion(
    child_id: int, 
    subject: Optional[str] = Query(None, description="Optional subject e.g. Mathematics"),
    estimated_minutes: Optional[int] = Query(None, description="Optional estimated minutes for new assignment"),
    db: Session = Depends(get_db)
):
    """Predicts actual homework completion time based on historical actual vs estimated logs."""
    return predictor.predict_homework_completion(
        db=db, child_id=child_id, subject=subject, estimated_minutes=estimated_minutes
    )


@router.get("/children/predict/attendance/{child_id}", response_model=PredictionResponse)
def predict_attendance_trend(child_id: int, db: Session = Depends(get_db)):
    """Predicts upcoming attendance trend and probability based on historical attendance logs."""
    return predictor.predict_attendance_trend(db=db, child_id=child_id)


@router.get("/children/predict/study/{child_id}", response_model=PredictionResponse)
def predict_study_performance_trend(child_id: int, db: Session = Depends(get_db)):
    """Predicts study performance index based on study sessions and exam results."""
    return predictor.predict_study_performance(db=db, child_id=child_id)


@router.get("/children/predict/screen-time/{child_id}", response_model=PredictionResponse)
def predict_screen_time_trend(child_id: int, db: Session = Depends(get_db)):
    """Predicts expected daily screen time and limit risk based on historical screen time logs."""
    return predictor.predict_screen_time_trend(db=db, child_id=child_id)


@router.get("/children/predict/routine/{child_id}", response_model=PredictionResponse)
def predict_routine_balance(child_id: int, db: Session = Depends(get_db)):
    """Predicts sleep consistency and overall routine balance score based on health logs and activities."""
    return predictor.predict_routine_balance(db=db, child_id=child_id)
