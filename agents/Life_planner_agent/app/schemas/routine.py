import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.routine import RoutinePriority, RoutineStatus

class FamilyRoutineBase(BaseModel):
    member_name: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    scheduled_start: datetime.datetime
    scheduled_end: datetime.datetime
    priority: RoutinePriority = RoutinePriority.MEDIUM
    status: RoutineStatus = RoutineStatus.PLANNED
    category: Optional[str] = "GENERAL"

class FamilyRoutineCreate(FamilyRoutineBase):
    family_id: str = Field("default_family", max_length=100)

class FamilyRoutineUpdate(BaseModel):
    member_name: Optional[str] = Field(None, min_length=1, max_length=100)
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    scheduled_start: Optional[datetime.datetime] = None
    scheduled_end: Optional[datetime.datetime] = None
    priority: Optional[RoutinePriority] = None
    status: Optional[RoutineStatus] = None
    category: Optional[str] = None

class FamilyRoutineResponse(FamilyRoutineBase):
    id: int
    family_id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
