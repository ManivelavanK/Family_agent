from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ChildInsight(BaseModel):
    event_type: str = Field(..., description="Type of detected event e.g. HOMEWORK_OVERDUE, EXCESSIVE_SCREEN_TIME, EXAM_APPROACHING")
    severity: str = Field("MEDIUM", description="HIGH, MEDIUM, LOW, CRITICAL")
    child_id: int = Field(..., description="ID of child profile")
    explanation: str = Field(..., description="Human-readable explanation of detected event")
    evidence: Dict[str, Any] = Field(default_factory=dict, description="Contextual evidence data points supporting this insight")
    recommended_action: str = Field(..., description="Suggested proactive intervention for child or parent")
    parent_notification_required: bool = Field(False, description="Whether parent should be notified")
    child_notification_required: bool = Field(True, description="Whether child should receive notification")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ProactiveAnalysisReport(BaseModel):
    child_id: int
    total_insights_detected: int = 0
    new_insights_logged: int = 0
    cooldown_skipped_insights: int = 0
    insights: List[ChildInsight] = Field(default_factory=list)
