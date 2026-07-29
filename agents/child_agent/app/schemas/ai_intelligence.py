from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ChildAIInsight(BaseModel):
    child_id: int
    insight_type: str = Field(..., description="ACADEMIC, STUDY_CONSISTENCY, HOMEWORK_RISK, EXAM_RISK, ATTENDANCE_RISK, SCREEN_TIME_IMBALANCE, ROUTINE_IMBALANCE, FINANCIAL_PATTERN, WELLNESS_CONCERN, POSITIVE_ACHIEVEMENT")
    severity: str = Field("MEDIUM", description="LOW, MEDIUM, HIGH, CRITICAL")
    title: str = Field(..., description="Short title of the insight")
    explanation: str = Field(..., description="Detailed explanation of the insight")
    evidence: List[str] = Field(default_factory=list, description="Key data points supporting this insight")
    recommendation: str = Field(..., description="Actionable recommendation")
    suggested_action: str = Field(..., description="Specific step to take")
    parent_notification_required: bool = Field(False)
    child_notification: str = Field(..., description="Encouraging message for child")
    confidence: float = Field(0.9, description="Confidence score from 0.0 to 1.0")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ParentNotificationDecision(BaseModel):
    should_notify: bool = Field(False)
    notification_type: str = Field("WEEKLY_CHILD_SUMMARY")
    severity: str = Field("MEDIUM")
    safe_message: str = Field(..., description="Privacy-safe summary message for parent")
    reason: str = Field(..., description="Reason for notification decision")
    channel: str = Field("WHATSAPP")


class ChildAIIntelligenceReport(BaseModel):
    child_id: int
    overall_status: str = Field("GOOD", description="EXCELLENT, GOOD, MODERATE, NEEDS_ATTENTION")
    key_insights: List[ChildAIInsight] = Field(default_factory=list)
    academic_status: Dict[str, Any] = Field(default_factory=dict)
    wellbeing_status: Dict[str, Any] = Field(default_factory=dict)
    routine_status: Dict[str, Any] = Field(default_factory=dict)
    financial_status: Dict[str, Any] = Field(default_factory=dict)
    safety_status: Dict[str, Any] = Field(default_factory=dict)
    recommended_actions: List[str] = Field(default_factory=list)
    parent_notification_decision: ParentNotificationDecision
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
