import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.models.plan import PlanType, PlanStatus, TaskPriority, TaskStatus, BudgetStatus

# --- TASK SCHEMAS ---
class PlanTaskBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    due_date: Optional[datetime.date] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    estimated_cost: float = Field(0.0, ge=0.0)

class PlanTaskCreate(PlanTaskBase):
    pass

class PlanTaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    due_date: Optional[datetime.date] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    estimated_cost: Optional[float] = Field(None, ge=0.0)

class PlanTaskResponse(PlanTaskBase):
    id: int
    plan_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

# --- BUDGET ITEM SCHEMAS ---
class BudgetItemBase(BaseModel):
    category: str = Field(..., max_length=100)
    description: Optional[str] = None
    estimated_amount: float = Field(0.0, ge=0.0)
    actual_amount: float = Field(0.0, ge=0.0)
    status: BudgetStatus = BudgetStatus.ESTIMATED

class BudgetItemCreate(BudgetItemBase):
    pass

class BudgetItemUpdate(BaseModel):
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    estimated_amount: Optional[float] = Field(None, ge=0.0)
    actual_amount: Optional[float] = Field(None, ge=0.0)
    status: Optional[BudgetStatus] = None

class BudgetItemResponse(BudgetItemBase):
    id: int
    plan_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

# --- ITINERARY ITEM SCHEMAS ---
class ItineraryItemBase(BaseModel):
    date: datetime.date
    start_time: Optional[datetime.time] = None
    end_time: Optional[datetime.time] = None
    activity: str = Field(..., max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    estimated_cost: float = Field(0.0, ge=0.0)
    notes: Optional[str] = None

class ItineraryItemCreate(ItineraryItemBase):
    pass

class ItineraryItemUpdate(BaseModel):
    date: Optional[datetime.date] = None
    start_time: Optional[datetime.time] = None
    end_time: Optional[datetime.time] = None
    activity: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    estimated_cost: Optional[float] = Field(None, ge=0.0)
    notes: Optional[str] = None

class ItineraryItemResponse(ItineraryItemBase):
    id: int
    plan_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

# --- PARTICIPANT SCHEMAS ---
class ParticipantBase(BaseModel):
    name: str = Field(..., max_length=255)
    age: Optional[int] = Field(None, ge=0, le=150)
    relationship: Optional[str] = Field(None, max_length=100)
    special_requirements: Optional[str] = None

class ParticipantCreate(ParticipantBase):
    pass

class ParticipantUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    age: Optional[int] = Field(None, ge=0, le=150)
    relationship: Optional[str] = Field(None, max_length=100)
    special_requirements: Optional[str] = None

class ParticipantResponse(ParticipantBase):
    id: int
    plan_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

# --- PLAN SCHEMAS ---
class PlanBase(BaseModel):
    plan_type: PlanType
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None
    number_of_people: int = Field(1, ge=1)
    budget: float = Field(0.0, ge=0.0)
    status: PlanStatus = PlanStatus.DRAFT
    location: Optional[str] = Field(None, max_length=255)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date cannot be before start_date")
        return self

class PlanCreate(PlanBase):
    pass

class PlanUpdate(BaseModel):
    plan_type: Optional[PlanType] = None
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None
    number_of_people: Optional[int] = Field(None, ge=1)
    budget: Optional[float] = Field(None, ge=0.0)
    status: Optional[PlanStatus] = None
    location: Optional[str] = Field(None, max_length=255)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date cannot be before start_date")
        return self

class PlanResponse(PlanBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    tasks: List[PlanTaskResponse] = []
    budget_items: List[BudgetItemResponse] = []
    itinerary_items: List[ItineraryItemResponse] = []
    participants: List[ParticipantResponse] = []

    model_config = ConfigDict(from_attributes=True)
