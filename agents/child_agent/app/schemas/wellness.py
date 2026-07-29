from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


# --- Diary Schemas ---

class DiaryEntryBase(BaseModel):
    child_id: int
    date: date
    title: str
    content: str
    mood: Optional[str] = Field(None, description="e.g. happy, calm, anxious, sad, angry, stressed")
    tags: Optional[List[str]] = Field(default_factory=list)
    share_with_parent: Optional[bool] = Field(default=False, description="Privacy toggle, default False")

class DiaryEntryCreate(DiaryEntryBase):
    pass

class DiaryEntryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    mood: Optional[str] = None
    tags: Optional[List[str]] = None
    share_with_parent: Optional[bool] = None

class DiaryEntryResponse(DiaryEntryBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


# --- Relaxation & Wellbeing Schemas ---

class RelaxationActivity(BaseModel):
    type: str = Field(..., description="breathing, short walk, music, stretching, meditation, hobby, journaling, screen break, social connection")
    title: str
    description: str
    suggested_duration_minutes: int
    target_age_group: str
    category: str


class RelaxationResponse(BaseModel):
    child_id: int
    age: int
    age_group: str
    suggested_activities: List[RelaxationActivity]
    mood_trend_summary: Optional[str] = None
    support_recommendation: Optional[str] = None
    privacy_disclaimer: str = Field(
        default="Diary entries are strictly private to the child and kept separate from analytics and automated parent reports unless explicitly enabled."
    )
    medical_disclaimer: str = Field(
        default="This system provides supportive wellbeing suggestions and does NOT provide medical or mental health diagnoses."
    )


class RelaxationLogCreate(BaseModel):
    child_id: int
    date: date
    activity_type: str
    duration_minutes: Optional[int] = None
    mood_before: Optional[str] = None
    mood_after: Optional[str] = None
    notes: Optional[str] = None

class RelaxationLogResponse(RelaxationLogCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)
