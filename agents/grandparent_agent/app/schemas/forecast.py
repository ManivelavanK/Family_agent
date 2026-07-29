from pydantic import BaseModel
from datetime import date
from typing import List


class ForecastPoint(BaseModel):
    date: date
    predicted_blood_pressure_systolic: float
    predicted_blood_sugar: float


class VitalsForecastResponse(BaseModel):
    metric: str
    predictions: List[ForecastPoint]
    model_trained: bool
