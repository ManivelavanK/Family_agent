import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class PlanReflectionBase(BaseModel):
    plan_id: int
    rating: int = Field(5, ge=1, le=5)
    what_went_well: Optional[str] = None
    what_went_wrong: Optional[str] = None
    feedback: Optional[str] = None
    future_suggestions: Optional[str] = None

class PlanReflectionCreate(PlanReflectionBase):
    pass

class PlanReflectionResponse(PlanReflectionBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
