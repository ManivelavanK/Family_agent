from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class PredictionResponse(BaseModel):
    child_id: int
    prediction_type: str = Field(..., description="homework, attendance, study, screen-time, routine")
    has_sufficient_data: bool
    sample_count: int
    prediction: Optional[Any] = Field(None, description="Predicted numerical value or formatted trend result")
    unit: Optional[str] = Field(None, description="e.g. minutes, %, points")
    confidence: str = Field(..., description="HIGH, MEDIUM, LOW, NONE")
    quality_indicator: str = Field(..., description="EXCELLENT, GOOD, FAIR, POOR, INSUFFICIENT")
    explanation: str
    details: Optional[Dict[str, Any]] = Field(default_factory=dict)
    model_config = ConfigDict(from_attributes=True)


class MLTrainResponse(BaseModel):
    status: str
    models_trained: List[str]
    training_details: Dict[str, Any]
    trained_at: datetime
    model_config = ConfigDict(from_attributes=True)
