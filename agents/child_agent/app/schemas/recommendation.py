from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    child_id: int
    include_ml_predictions: bool = Field(True, description="Whether to include ML predictor insights in context")
    focus_areas: Optional[List[str]] = Field(
        None, 
        description="Optional focus areas: study, homework, time_management, health, screen_time, pocket_money, safety, relaxation"
    )


class ComprehensiveRecommendation(BaseModel):
    study_suggestions: List[str] = Field(default_factory=list)
    homework_prioritization: List[str] = Field(default_factory=list)
    time_management: List[str] = Field(default_factory=list)
    daily_motivation: str = Field(...)
    healthy_routine_advice: List[str] = Field(default_factory=list)
    screen_time_advice: List[str] = Field(default_factory=list)
    saving_suggestions: List[str] = Field(default_factory=list)
    parent_recommendations: List[str] = Field(default_factory=list)
    exam_preparation_suggestions: List[str] = Field(default_factory=list)
    relaxation_suggestions: List[str] = Field(default_factory=list)


class RecommendationResponse(BaseModel):
    child_id: int
    child_name: str
    age: int
    age_group: str
    education_stage: str
    deterministic_summary: Dict[str, Any]
    ml_predictions: Optional[Dict[str, Any]] = None
    ai_recommendations: ComprehensiveRecommendation
    generated_by: str
    disclaimer: str = Field(
        "AI recommendations are for guidance only. They do not constitute medical, health, or psychological diagnosis."
    )
