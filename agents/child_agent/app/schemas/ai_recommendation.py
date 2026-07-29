from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class DetailedRecommendationItem(BaseModel):
    category: str = Field(..., description="Domain category: academic, homework, study_habits, focus, exams, attendance, screen_time, routine, activities, financial, wellness, safety")
    title: str = Field(..., description="Short descriptive title of recommendation")
    explanation: str = Field(..., description="Detailed contextual explanation")
    priority: str = Field("MEDIUM", description="HIGH, MEDIUM, LOW")
    suggested_action: str = Field(..., description="Concrete actionable advice for child or parent")
    reason: str = Field(..., description="Reasoning based on child context indicators")
    confidence: str = Field("HIGH", description="HIGH, MEDIUM, LOW")
    requires_parent_attention: bool = Field(False, description="Whether parent should be notified or review")
    requires_immediate_action: bool = Field(False, description="Whether immediate action is required")
    source_data: List[str] = Field(default_factory=list, description="Data points/fields used for this recommendation")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ChildRecommendationEngineOutput(BaseModel):
    child_id: int
    recommendations: List[DetailedRecommendationItem] = Field(default_factory=list)
    generated_by: str = Field("Groq AI Engine")
    disclaimer: str = Field("AI recommendations are for guidance only. Safety alerts and balances are calculated deterministically.")
