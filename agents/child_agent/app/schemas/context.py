from typing import List, Optional, Dict, Any
from datetime import date, time, datetime
from pydantic import BaseModel, Field


class PrivacyFilteredProfile(BaseModel):
    child_id: int
    name: str
    age: int
    age_group: str
    education_stage: str
    class_or_year: Optional[str] = None
    interests: List[str] = Field(default_factory=list)
    career_interest: Optional[str] = None
    daily_wake_time: Optional[str] = None
    daily_sleep_time: Optional[str] = None


class HomeworkSummaryContext(BaseModel):
    total_count: int = 0
    pending_count: int = 0
    completed_count: int = 0
    overdue_count: int = 0
    high_priority_count: int = 0
    pending_subjects: List[str] = Field(default_factory=list)
    overdue_items: List[Dict[str, Any]] = Field(default_factory=list)


class StudySummaryContext(BaseModel):
    total_sessions: int = 0
    total_study_minutes: int = 0
    avg_session_minutes: float = 0.0
    avg_focus_score: Optional[float] = None
    materials_count: int = 0
    recent_subjects_studied: List[str] = Field(default_factory=list)


class ExamSummaryContext(BaseModel):
    total_exams: int = 0
    upcoming_count: int = 0
    avg_exam_percentage: Optional[float] = None
    upcoming_exams: List[Dict[str, Any]] = Field(default_factory=list)


class AttendanceSummaryContext(BaseModel):
    total_days: int = 0
    present_days: int = 0
    absent_days: int = 0
    attendance_percentage: float = 100.0


class ScreenTimeSummaryContext(BaseModel):
    avg_daily_minutes: float = 0.0
    avg_educational_minutes: float = 0.0
    late_night_count: int = 0
    screen_time_exceeded: bool = False


class HealthRoutineSummaryContext(BaseModel):
    avg_sleep_hours: float = 8.0
    avg_water_intake_ml: int = 1500
    avg_activity_minutes: int = 30
    health_alerts_count: int = 0


class ActivitiesSummaryContext(BaseModel):
    total_activities_count: int = 0
    upcoming_activities: List[Dict[str, Any]] = Field(default_factory=list)


class PocketMoneySummaryContext(BaseModel):
    allowance_total: float = 0.0
    total_spent: float = 0.0
    total_saved: float = 0.0
    active_goals_count: int = 0
    saving_goals: List[Dict[str, Any]] = Field(default_factory=list)


class SafetySummaryContext(BaseModel):
    check_in_status: str = "SAFE"
    emergency_contact_registered: bool = False
    active_alerts_count: int = 0
    last_check_in_note: Optional[str] = None


class NutritionSummaryContext(BaseModel):
    breakfast_consistency_pct: float = 100.0
    avg_water_ml: int = 1500
    bridge_events_count: int = 0


class ScheduleSummaryContext(BaseModel):
    today_items_count: int = 0
    upcoming_holidays_count: int = 0
    today_schedule: List[Dict[str, Any]] = Field(default_factory=list)


class RecentNotificationContext(BaseModel):
    id: int
    title: str
    message: str
    notification_type: str
    created_at: str


class PreviousRecommendationContext(BaseModel):
    daily_motivation: Optional[str] = None
    study_suggestions: List[str] = Field(default_factory=list)
    healthy_routine_advice: List[str] = Field(default_factory=list)
    screen_time_advice: List[str] = Field(default_factory=list)
    parent_recommendations: List[str] = Field(default_factory=list)


class ChildContext(BaseModel):
    profile: PrivacyFilteredProfile
    homework: HomeworkSummaryContext = Field(default_factory=HomeworkSummaryContext)
    study: StudySummaryContext = Field(default_factory=StudySummaryContext)
    exams: ExamSummaryContext = Field(default_factory=ExamSummaryContext)
    attendance: AttendanceSummaryContext = Field(default_factory=AttendanceSummaryContext)
    screen_time: ScreenTimeSummaryContext = Field(default_factory=ScreenTimeSummaryContext)
    health: HealthRoutineSummaryContext = Field(default_factory=HealthRoutineSummaryContext)
    activities: ActivitiesSummaryContext = Field(default_factory=ActivitiesSummaryContext)
    pocket_money: PocketMoneySummaryContext = Field(default_factory=PocketMoneySummaryContext)
    safety: SafetySummaryContext = Field(default_factory=SafetySummaryContext)
    nutrition: NutritionSummaryContext = Field(default_factory=NutritionSummaryContext)
    schedule: ScheduleSummaryContext = Field(default_factory=ScheduleSummaryContext)
    recent_notifications: List[RecentNotificationContext] = Field(default_factory=list)
    previous_recommendations: Optional[PreviousRecommendationContext] = None
    ml_predictions: Optional[Dict[str, Any]] = None
