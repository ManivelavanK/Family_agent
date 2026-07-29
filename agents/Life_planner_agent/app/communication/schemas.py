from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field

class AgentCapabilities(BaseModel):
    name: str
    base_url: str
    capabilities: List[str] = []
    is_mock: bool = True

class FatherContext(BaseModel):
    available_budget: Optional[float] = None
    monthly_savings_goal: Optional[float] = None
    financial_notes: Optional[str] = None
    source: str = "Father Agent"

class MotherContext(BaseModel):
    food_preferences: List[str] = []
    grocery_budget_limit: Optional[float] = None
    dietary_restrictions: List[str] = []
    source: str = "Mother Agent"

class ChildContext(BaseModel):
    upcoming_exams: List[Dict[str, Any]] = []
    extracurricular_schedule: List[Dict[str, Any]] = []
    school_vacation_dates: List[Dict[str, Any]] = []
    source: str = "Child Agent"

class GrandparentContext(BaseModel):
    mobility_level: Optional[str] = None  # e.g., "LOW_WALKING", "WHEELCHAIR_ACCESSIBLE"
    doctor_appointments: List[Dict[str, Any]] = []
    health_notes: Optional[str] = None
    source: str = "Grandparent Agent"

class BabyContext(BaseModel):
    feeding_schedule: Optional[str] = None
    sleep_routine: Optional[str] = None
    special_care_notes: Optional[str] = None
    source: str = "Baby Care Agent"

class FamilyAgentContext(BaseModel):
    family_id: str
    father: Optional[FatherContext] = None
    mother: Optional[MotherContext] = None
    child: Optional[ChildContext] = None
    grandparent: Optional[GrandparentContext] = None
    baby: Optional[BabyContext] = None
    available_sources: List[str] = []
    unavailable_sources: List[str] = []
    retrieval_errors: List[str] = []

    model_config = ConfigDict(from_attributes=True)
