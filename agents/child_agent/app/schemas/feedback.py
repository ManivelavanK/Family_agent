from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class RecommendationOutcome(BaseModel):
    recommendation_id: str
    child_id: int
    category: str
    suggested_action: str
    observed_action: Optional[str] = None
    outcome_status: str = Field("PENDING", description="PENDING, SUCCESSFUL, PARTIAL, IGNORED, INEFFECTIVE")
    effectiveness_score: float = Field(0.0, description="Score from 0.0 to 100.0")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    evaluated_at: Optional[str] = None


class ChildPersonalizationProfile(BaseModel):
    child_id: int
    optimal_study_duration_mins: int = 45
    preferred_study_time: str = "AFTERNOON"  # MORNING, AFTERNOON, EVENING
    planning_style: str = "BALANCED"  # STRICT_POMODORO, BALANCED, FLEXIBLE
    reminder_frequency: str = "MODERATE"  # LOW, MODERATE, HIGH
    recommendation_difficulty: str = "MODERATE"  # EASY, MODERATE, CHALLENGING
    communication_style: str = "ENCOURAGING"  # DIRECT, ENCOURAGING, PLAYFUL
    ignored_patterns_count: Dict[str, int] = Field(default_factory=dict)
    successful_categories_count: Dict[str, int] = Field(default_factory=dict)
