from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AIDailyDashboardResponse(BaseModel):
    child_id: int
    greeting: str
    overall_status: str = Field(..., description="Overall child wellbeing and academic status summary (e.g., 'GOOD', 'NEEDS_ATTENTION', 'EXCELLENT')")
    todays_priorities: List[str] = Field(default_factory=list, description="Top 3-4 priorities for the day")
    homework_status: Dict[str, Any] = Field(default_factory=dict, description="Pending, completed, and overdue homework metrics")
    upcoming_deadlines: List[Dict[str, Any]] = Field(default_factory=list, description="Upcoming assignments and exam deadlines")
    exam_preparation_status: Dict[str, Any] = Field(default_factory=dict, description="Upcoming exams and preparation level")
    recommended_study_plan: List[str] = Field(default_factory=list, description="Structured hourly/session study advice")
    study_performance: Dict[str, Any] = Field(default_factory=dict, description="Focus score and study session stats")
    screen_time_summary: Dict[str, Any] = Field(default_factory=dict, description="Daily average and recreational screen time stats")
    wellness_routine_status: Dict[str, Any] = Field(default_factory=dict, description="Sleep, water, and routine metrics")
    pocket_money_status: Dict[str, Any] = Field(default_factory=dict, description="Remaining balance and saving goal progress")
    safety_status: Dict[str, Any] = Field(default_factory=dict, description="Check-in status and return times")
    important_alerts: List[str] = Field(default_factory=list, description="High-priority alerts and warnings")
    what_should_i_do_today: List[str] = Field(default_factory=list, description="AI-generated actionable guide for child")
    what_should_parent_know: List[str] = Field(default_factory=list, description="AI-generated privacy-aware summary for parents")

    # Backward compatibility fields matching original DailyDashboardResponse
    timetable: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    aggregated_data: Dict[str, Any] = Field(default_factory=dict)
