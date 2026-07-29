from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class ExamBase(BaseModel):
    child_id: int
    subject: str
    exam_name: str
    exam_date: date
    syllabus: Optional[str] = None
    preparation_percentage: int = Field(0, ge=0, le=100)
    difficulty: str = Field("Medium", description="Easy, Medium, Hard")
    notes: Optional[str] = None

class ExamCreate(ExamBase):
    pass

class ExamUpdate(BaseModel):
    subject: Optional[str] = None
    exam_name: Optional[str] = None
    exam_date: Optional[date] = None
    syllabus: Optional[str] = None
    preparation_percentage: Optional[int] = Field(None, ge=0, le=100)
    difficulty: Optional[str] = None
    notes: Optional[str] = None

class ExamResponse(ExamBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class ExamCountdownResponse(BaseModel):
    id: int
    subject: str
    exam_name: str
    exam_date: date
    days_remaining: int
    preparation_percentage: int
    syllabus_completion: int  # equivalent to preparation_percentage
    priority: str  # HIGH, MEDIUM, LOW

class ExamStudyPlanResponse(BaseModel):
    exam_name: str
    subject: str
    days_remaining: int
    difficulty: str
    current_preparation: int
    recommended_daily_study_hours: float
    preparation_plan: List[str]
