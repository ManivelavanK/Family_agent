from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class HomeworkBase(BaseModel):
    family_id: str
    child_id: int
    subject: str
    title: str
    description: Optional[str] = None
    assigned_date: date
    due_date: date
    priority: str = Field("MEDIUM", description="HIGH, MEDIUM, or LOW")
    estimated_minutes: Optional[int] = Field(None, ge=0)
    actual_minutes: Optional[int] = Field(None, ge=0)

class HomeworkCreate(HomeworkBase):
    pass

class HomeworkUpdate(BaseModel):
    family_id: Optional[str] = None
    child_id: Optional[int] = None
    subject: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_date: Optional[date] = None
    due_date: Optional[date] = None
    priority: Optional[str] = None
    estimated_minutes: Optional[int] = None
    actual_minutes: Optional[int] = None
    completion_status: Optional[bool] = None
    completion_date: Optional[date] = None

class HomeworkResponse(HomeworkBase):
    id: int
    completion_status: bool
    completion_date: Optional[date] = None


    model_config = ConfigDict(from_attributes=True)

class HomeworkPlanningRecommendations(BaseModel):
    child_id: int
    education_stage: str
    planning_style: str  # e.g., "Subject-Based Homework Planning" or "Assignments, Projects, Labs & Deadlines"
    tips: List[str]
