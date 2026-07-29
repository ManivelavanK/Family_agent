from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class InterventionAction(BaseModel):
    agent_name: str = Field(..., description="Name of executing agent e.g. StudyCoachAgent, ScreenTimeAgent")
    target_role: str = Field(..., description="Target: CHILD, PARENT, SCHEDULE, SYSTEM")
    action_type: str = Field(..., description="RECOMMEND_SCHEDULE, RECOMMEND_SCREEN_REDUCTION, DRAFT_PARENT_SUMMARY, SHOW_ENCOURAGEMENT, ADD_STUDY_BLOCK")
    description: str = Field(..., description="Human readable description of proposed action")
    requires_parent_consent: bool = Field(False, description="Whether explicit parent consent is required")
    requires_child_consent: bool = Field(False, description="Whether explicit child consent is required")
    status: str = Field("PROPOSED", description="PROPOSED, APPROVED, EXECUTED, REJECTED")


class InterventionPlan(BaseModel):
    intervention_id: Optional[str] = None
    child_id: int
    problem: str = Field(..., description="Synthesized multi-domain problem statement")
    evidence: List[str] = Field(default_factory=list, description="Data points supporting intervention trigger")
    selected_agents: List[str] = Field(default_factory=list, description="List of coordinating agent names")
    actions: List[InterventionAction] = Field(default_factory=list, description="Coordinated action plan")
    child_message: str = Field(..., description="Encouraging, supportive message for child")
    parent_message: str = Field(..., description="Privacy-safe summary & recommendations for parent")
    priority: str = Field("HIGH", description="CRITICAL, HIGH, MEDIUM, LOW")
    expected_outcome: str = Field(..., description="Target outcome expected from intervention")
    follow_up_time: str = Field(..., description="ISO timestamp or relative time for follow-up evaluation")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class InterventionHistoryRecord(BaseModel):
    intervention_id: str
    child_id: int
    problem: str
    priority: str
    status: str = Field("ACTIVE", description="ACTIVE, COMPLETED, RESOLVED, REJECTED")
    outcome_rating: Optional[str] = Field(None, description="IMPROVED, NEUTRAL, UNRESOLVED")
    created_at: str
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
