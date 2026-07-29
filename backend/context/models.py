from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

# ── 1. Category Data Models ──────────────────────────────────────────────────

class FamilyProfile(BaseModel):
    family_id: str = "default_family"
    family_name: str = "KinNest Family"
    members: List[str] = Field(default_factory=list)
    active_admin: str = ""
    family_password_hash: str = ""
    created_date: datetime = Field(default_factory=datetime.utcnow)

class ShoppingItem(BaseModel):
    name: str
    quantity: str = "1"
    status: str = "PENDING"  # PENDING or PURCHASED
    requested_by: str = ""

class ShoppingContext(BaseModel):
    shared_shopping_list: List[ShoppingItem] = Field(default_factory=list)
    total_estimated_cost: float = 0.0
    last_updated_by: str = ""

class PurchaseRequest(BaseModel):
    request_id: str
    item_name: str
    amount: float
    requested_by: str
    status: str = "PENDING"  # PENDING, APPROVED, REJECTED

class BudgetContext(BaseModel):
    monthly_budget: float = 0.0
    weekly_budget: float = 0.0
    current_spending: float = 0.0
    remaining_budget: float = 0.0
    pending_purchase_requests: List[PurchaseRequest] = Field(default_factory=list)

class ActiveEmergency(BaseModel):
    emergency_id: str
    description: str
    severity: str = "HIGH"  # MEDIUM, HIGH, CRITICAL
    reported_at: datetime = Field(default_factory=datetime.utcnow)
    resolved: bool = False

class MedicineReminder(BaseModel):
    medicine_name: str
    dosage: str
    scheduled_time: str
    taken: bool = False

class HealthContext(BaseModel):
    active_emergencies: List[ActiveEmergency] = Field(default_factory=list)
    grandparent_alerts: List[str] = Field(default_factory=list)
    medicine_reminders: List[MedicineReminder] = Field(default_factory=list)
    upcoming_appointments: List[Dict[str, Any]] = Field(default_factory=list)
    health_summary: str = ""

class ChildContext(BaseModel):
    homework_status: Dict[str, str] = Field(default_factory=dict) # homework_id -> status (PENDING/COMPLETED)
    attendance: Dict[str, str] = Field(default_factory=dict)     # date -> status
    exams: List[Dict[str, Any]] = Field(default_factory=list)
    study_progress: Dict[str, Any] = Field(default_factory=dict)
    parent_notifications: List[str] = Field(default_factory=list)

class BabyContext(BaseModel):
    feeding_schedule: List[Dict[str, Any]] = Field(default_factory=list)
    sleep_schedule: List[Dict[str, Any]] = Field(default_factory=list)
    vaccinations: List[Dict[str, Any]] = Field(default_factory=list)
    growth_milestones: List[Dict[str, Any]] = Field(default_factory=list)
    diaper_records: List[Dict[str, Any]] = Field(default_factory=list)

class PlannerContext(BaseModel):
    today_tasks: List[Dict[str, Any]] = Field(default_factory=list)
    family_events: List[Dict[str, Any]] = Field(default_factory=list)
    upcoming_meetings: List[Dict[str, Any]] = Field(default_factory=list)
    shared_calendar: List[Dict[str, Any]] = Field(default_factory=list)
    pending_workflows: List[Dict[str, Any]] = Field(default_factory=list)

# ── 2. Audit and Wrapper Models ──────────────────────────────────────────────

class AuditEvent(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_name: str
    category: str
    operation: str  # READ, WRITE, PATCH, DELETE
    details: Dict[str, Any] = Field(default_factory=dict)

class ContextWrapper(BaseModel):
    category: str
    data: Dict[str, Any]
    version: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    last_updated_by: str = "unknown"
