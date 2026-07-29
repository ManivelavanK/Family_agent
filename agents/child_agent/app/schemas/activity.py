from datetime import date, time
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class ActivityBase(BaseModel):
    child_id: int
    title: str
    activity_type: str = Field(..., description="Tuition, Sports, Music, Dance, Competition, Club, College project, Study group, Family event, Other")
    date: date
    start_time: time
    end_time: time
    location: Optional[str] = None
    priority: str = Field("Medium", description="Low, Medium, High")

class ActivityCreate(ActivityBase):
    pass

class ActivityResponse(ActivityBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class AgendaItem(BaseModel):
    title: str
    type: str  # Sleep, Meal, School, College, Homework, Exam Prep, Study Session, Activity
    start_time: time
    end_time: time
    priority: str
    is_conflict: bool = False
    conflict_description: Optional[str] = None

class AgendaDay(BaseModel):
    date: date
    items: List[AgendaItem]
    total_conflicting_items: int
