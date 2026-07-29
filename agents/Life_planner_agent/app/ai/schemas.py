import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field
from app.models.plan import PlanType, PlanStatus, TaskPriority, BudgetStatus

class AIRequirements(BaseModel):
    destination: Optional[str] = None
    duration_days: Optional[int] = Field(None, ge=1)
    people: Optional[int] = Field(None, ge=1)
    budget: Optional[float] = Field(None, ge=0.0)
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None
    location: Optional[str] = None
    special_notes: Optional[str] = None

class AITaskDraft(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime.date] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    estimated_cost: float = 0.0

class AIBudgetItemDraft(BaseModel):
    category: str
    description: Optional[str] = None
    estimated_amount: float = 0.0
    status: BudgetStatus = BudgetStatus.ESTIMATED

class AIItineraryItemDraft(BaseModel):
    date: datetime.date
    start_time: Optional[datetime.time] = None
    end_time: Optional[datetime.time] = None
    activity: str
    location: Optional[str] = None
    estimated_cost: float = 0.0
    notes: Optional[str] = None

class AIParticipantDraft(BaseModel):
    name: str
    age: Optional[int] = None
    relationship: Optional[str] = None
    special_requirements: Optional[str] = None

class AIPlanDraft(BaseModel):
    title: str
    plan_type: PlanType
    description: Optional[str] = None
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None
    number_of_people: int = 1
    budget: float = 0.0
    location: Optional[str] = None
    tasks: List[AITaskDraft] = []
    budget_breakdown: List[AIBudgetItemDraft] = []
    itinerary: List[AIItineraryItemDraft] = []
    participants: List[AIParticipantDraft] = []

class AIContextSelectionResponse(BaseModel):
    required_agent_domains: List[str] = []
    reasoning: str

    model_config = ConfigDict(from_attributes=True)

class AIPlanningResponse(BaseModel):
    plan_type: PlanType
    title: str
    intent: str
    requirements: AIRequirements
    missing_information: List[str] = []
    preferences: List[str] = []
    constraints: List[str] = []
    reasoning_summary: str
    recommendations: List[str] = []
    draft_plan: Optional[AIPlanDraft] = None
    next_action: str = Field(..., description="Action recommendation, e.g., 'NEED_MORE_INFO', 'GENERATE_DRAFT', 'APPROVE_PLAN'")
    family_context_used: List[str] = []
    context_influence: List[str] = []
    context_sources: List[str] = []

    model_config = ConfigDict(from_attributes=True)

# --- CALENDAR REASONING SCHEMAS ---
class AIAlternativeSlot(BaseModel):
    start: str
    end: str
    suitability_reason: str

class AIAffectedEvent(BaseModel):
    event_id: Optional[int] = None
    title: str
    start: str
    end: str
    event_type: str

class AICalendarReasoningRequest(BaseModel):
    message: str = Field(..., min_length=3, description="Natural language scheduling or availability query")
    requested_start: Optional[datetime.datetime] = None
    requested_end: Optional[datetime.datetime] = None

class AICalendarReasoningResponse(BaseModel):
    conflict_detected: bool
    conflict_summary: str
    affected_events: List[AIAffectedEvent] = []
    recommended_action: str = Field(..., description="Action, e.g., 'PROCEED', 'MOVE_EVENT', 'NEED_MORE_INFO'")
    alternative_slots: List[AIAlternativeSlot] = []
    reasoning: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    missing_information: List[str] = []
    next_action: str = Field(..., description="Action, e.g., 'REVIEW_RECOMMENDATION', 'PROVIDE_MORE_INFO'")

from app.schemas.memory import AIMemoryCandidate, AIMemoryExtractionResponse

# --- EXECUTION, REVISION, OPTIMIZATION & ANALYSIS SCHEMAS ---
class AIPlanExecutionRequest(BaseModel):
    approved: bool = Field(..., description="Explicit user approval required for database execution")
    family_id: str = Field("default_family", max_length=100)
    draft_plan: AIPlanDraft

class AIPlanExecutionSummary(BaseModel):
    plan_id: int
    created: Dict[str, int]
    message: str

class AIPlanRevisionRequest(BaseModel):
    plan_id: int
    message: str = Field(..., min_length=3, description="Revision instruction")
    family_id: str = Field("default_family", max_length=100)

class AIPlanRevisionResponse(BaseModel):
    revised_draft: AIPlanDraft
    changes_explanation: str
    calendar_impact: List[str] = []
    reasoning: str

    model_config = ConfigDict(from_attributes=True)

class AIPlanOptimizeRequest(BaseModel):
    plan_id: int
    optimization_goal: str = Field(..., min_length=3, description="Goal, e.g., reduce budget, less tiring, reduce travel time")
    family_id: str = Field("default_family", max_length=100)

class AIPlanOptimizeResponse(BaseModel):
    optimized_draft: AIPlanDraft
    optimization_summary: str
    reasoning: str

    model_config = ConfigDict(from_attributes=True)

class AIPlanQualityAnalysisResponse(BaseModel):
    budget_score: float = Field(..., ge=0.0, le=10.0)
    schedule_score: float = Field(..., ge=0.0, le=10.0)
    family_fit_score: float = Field(..., ge=0.0, le=10.0)
    preparation_score: float = Field(..., ge=0.0, le=10.0)
    risk_score: float = Field(..., ge=0.0, le=10.0)
    overall_score: float = Field(..., ge=0.0, le=10.0)
    strengths: List[str] = []
    concerns: List[str] = []
    recommendations: List[str] = []
    reasoning: str

    model_config = ConfigDict(from_attributes=True)

# --- PROACTIVE AI SCHEMAS ---
class AIProactiveInsight(BaseModel):
    title: str
    priority: str = Field(..., description="HIGH, MEDIUM, LOW")
    category: str = Field("GENERAL", description="EVENT_PREPARATION, TASK_OVERDUE, BUDGET_WARNING, MEMORY_RECURRENCE")
    reasoning: str
    supporting_facts: List[str] = []
    recommended_action: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    related_plan_id: Optional[int] = None
    related_event_id: Optional[int] = None
    related_task_id: Optional[int] = None

class AIProactiveAnalysisRequest(BaseModel):
    family_id: str = Field("default_family", max_length=100)
    lookahead_days: int = Field(30, ge=1, le=180)

class AIProactiveAnalysisResponse(BaseModel):
    insights: List[AIProactiveInsight] = []
    reasoning_summary: str
    evaluated_facts_count: int = 0

    model_config = ConfigDict(from_attributes=True)

# --- GUEST PLANNING SCHEMAS ---
class AIGuestProfile(BaseModel):
    name: str
    relationship: Optional[str] = None
    adults: int = 1
    children: int = 0
    arrival: Optional[str] = None
    departure: Optional[str] = None

class AIGuestPreparationTask(BaseModel):
    title: str
    category: str = Field("GENERAL", description="BEDROOM, GROCERY, CLEANING, TRANSPORT, ACTIVITIES")
    due_date: Optional[datetime.date] = None
    estimated_cost: float = 0.0

class AIGuestDayPlan(BaseModel):
    day_number: int
    date: Optional[datetime.date] = None
    focus: str
    morning_activity: str
    afternoon_activity: str
    evening_activity: str
    meals_plan: str

class AIGuestBudgetEstimate(BaseModel):
    category: str
    estimated_cost: float = 0.0
    notes: Optional[str] = None

class AIGuestStayPlan(BaseModel):
    guest_summary: str
    accommodation_plan: str
    food_plan: str
    transport_plan: str
    preparation_tasks: List[AIGuestPreparationTask] = []
    daily_itinerary: List[AIGuestDayPlan] = []
    budget_breakdown: List[AIGuestBudgetEstimate] = []
    children_activities: List[str] = []
    contingency_suggestions: List[str] = []

class AIGuestPlanningRequest(BaseModel):
    family_id: str = Field("default_family", max_length=100)
    message: str = Field(..., min_length=3, description="Natural language guest visit description")
    guest_id: Optional[int] = None

class AIGuestPlanningResponse(BaseModel):
    guest_profile: AIGuestProfile
    stay_plan: AIGuestStayPlan
    draft_plan: Optional[AIPlanDraft] = None
    missing_information: List[str] = []
    recommendations: List[str] = []
    reasoning: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    risks: List[str] = []
    supporting_facts: List[str] = []

    model_config = ConfigDict(from_attributes=True)

# --- TRAVEL PLANNING SCHEMAS ---
class AITravelRequirements(BaseModel):
    destination: Optional[str] = None
    origin: Optional[str] = None
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None
    duration_days: Optional[int] = Field(None, ge=1)
    traveler_count: Optional[int] = Field(None, ge=1)
    adults: Optional[int] = Field(None, ge=0)
    children: Optional[int] = Field(None, ge=0)
    infants: Optional[int] = Field(None, ge=0)
    budget: Optional[float] = Field(None, ge=0.0)
    transport_preference: Optional[str] = None
    accommodation_preference: Optional[str] = None
    trip_style: Optional[str] = None
    special_requirements: Optional[str] = None

class AITravelDayPlan(BaseModel):
    day_number: int
    date: Optional[datetime.date] = None
    focus: str
    morning: str
    afternoon: str
    evening: str
    meals: str
    travel_notes: Optional[str] = None
    estimated_daily_cost: float = 0.0
    family_considerations: Optional[str] = None

class AITravelBudgetEstimate(BaseModel):
    transport: float = 0.0
    accommodation: float = 0.0
    food: float = 0.0
    activities: float = 0.0
    local_transport: float = 0.0
    emergency_contingency: float = 0.0
    estimated_total: float = 0.0
    budget_assessment: str
    reasoning: str

class AIPackingCategory(BaseModel):
    category: str
    items: List[str] = []
    reasoning: str
    priority: str = Field("HIGH", description="HIGH, MEDIUM, LOW")

class AITravelRisk(BaseModel):
    risk: str
    severity: str = Field("MEDIUM", description="HIGH, MEDIUM, LOW")
    reasoning: str
    mitigation: str

class AITravelAlternative(BaseModel):
    title: str
    description: str
    tradeoffs: str
    estimated_cost: float = 0.0
    why_recommended: str

class AITravelPlan(BaseModel):
    title: str
    destination: str
    summary: str
    requirements: AITravelRequirements
    trip_style: str
    travel_pace: str = Field("BALANCED", description="RELAXED, BALANCED, BUSY, VERY_BUSY")
    daily_itinerary: List[AITravelDayPlan] = []
    budget: AITravelBudgetEstimate
    packing_list: List[AIPackingCategory] = []
    risks: List[AITravelRisk] = []
    plan_a_summary: str
    plan_b_contingency: AITravelAlternative
    alternatives: List[AITravelAlternative] = []
    family_considerations: List[str] = []
    calendar_considerations: List[str] = []
    memory_influences: List[str] = []

class AITravelPlanningRequest(BaseModel):
    family_id: str = Field("default_family", max_length=100)
    message: str = Field(..., min_length=3, description="Natural language travel request")
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None

class AITravelPlanningResponse(BaseModel):
    travel_plan: AITravelPlan
    draft_plan: Optional[AIPlanDraft] = None
    missing_information: List[str] = []
    recommendations: List[str] = []
    reasoning: str
    confidence: float = Field(..., ge=0.0, le=1.0)

    model_config = ConfigDict(from_attributes=True)

class AITravelReviseRequest(BaseModel):
    family_id: str = Field("default_family", max_length=100)
    message: str = Field(..., min_length=3)
    current_travel_plan: AITravelPlan

class AITravelOptimizeRequest(BaseModel):
    family_id: str = Field("default_family", max_length=100)
    message: str = Field(..., min_length=3)
    current_travel_plan: AITravelPlan

class AITravelQualityAnalysisResponse(BaseModel):
    family_suitability_score: float = Field(..., ge=0.0, le=10.0)
    itinerary_realism_score: float = Field(..., ge=0.0, le=10.0)
    budget_quality_score: float = Field(..., ge=0.0, le=10.0)
    travel_pace_score: float = Field(..., ge=0.0, le=10.0)
    overall_score: float = Field(..., ge=0.0, le=10.0)
    strengths: List[str] = []
    weaknesses: List[str] = []
    risks: List[str] = []
    improvements: List[str] = []
    reasoning: str
    confidence: float = Field(..., ge=0.0, le=1.0)

    model_config = ConfigDict(from_attributes=True)

# --- FAMILY ROUTINE SCHEMAS ---
class AIRoutineItem(BaseModel):
    member_name: str
    title: str
    category: str = "GENERAL"
    start_time: str = Field(..., description="HH:MM format, e.g. '09:00'")
    end_time: str = Field(..., description="HH:MM format, e.g. '10:00'")
    priority: str = Field("MEDIUM", description="LOW, MEDIUM, HIGH, CRITICAL")
    reason: str
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None

class AIRoutineConflict(BaseModel):
    member_name: str
    conflicting_items: List[str] = []
    conflict_reason: str
    suggested_resolution: str

class AIRoutinePlanningRequest(BaseModel):
    family_id: str = Field("default_family", max_length=100)
    message: str = Field(..., min_length=3, description="Natural language daily routine request")
    target_date: Optional[datetime.date] = None

class AIRoutinePlanningResponse(BaseModel):
    family_id: str
    target_date: datetime.date
    daily_summary: str
    routine_items: List[AIRoutineItem] = []
    conflicts: List[AIRoutineConflict] = []
    overloaded_members: List[str] = []
    recommendations: List[str] = []
    missing_information: List[str] = []
    reasoning: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    next_action: str = Field("REVIEW_RECOMMENDATION", description="REVIEW_RECOMMENDATION, CONFIRM, EXECUTE")

    model_config = ConfigDict(from_attributes=True)

__all__ = [
    "AIRequirements", "AITaskDraft", "AIBudgetItemDraft", "AIItineraryItemDraft",
    "AIParticipantDraft", "AIPlanDraft", "AIPlanningResponse", "AIContextSelectionResponse",
    "AIAlternativeSlot", "AIAffectedEvent", "AICalendarReasoningRequest", "AICalendarReasoningResponse",
    "AIMemoryCandidate", "AIMemoryExtractionResponse",
    "AIPlanExecutionRequest", "AIPlanExecutionSummary", "AIPlanRevisionRequest", "AIPlanRevisionResponse",
    "AIPlanOptimizeRequest", "AIPlanOptimizeResponse", "AIPlanQualityAnalysisResponse",
    "AIProactiveInsight", "AIProactiveAnalysisRequest", "AIProactiveAnalysisResponse",
    "AIGuestProfile", "AIGuestPreparationTask", "AIGuestDayPlan", "AIGuestBudgetEstimate",
    "AIGuestStayPlan", "AIGuestPlanningRequest", "AIGuestPlanningResponse",
    "AITravelRequirements", "AITravelDayPlan", "AITravelBudgetEstimate", "AIPackingCategory",
    "AITravelRisk", "AITravelAlternative", "AITravelPlan", "AITravelPlanningRequest",
    "AITravelPlanningResponse", "AITravelReviseRequest", "AITravelOptimizeRequest", "AITravelQualityAnalysisResponse",
    "AIRoutineItem", "AIRoutineConflict", "AIRoutinePlanningRequest", "AIRoutinePlanningResponse"
]
