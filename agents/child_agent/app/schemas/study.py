from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, ConfigDict

class StudyMaterialBase(BaseModel):
    child_id: int
    subject: str
    title: str
    material_type: str = Field(..., description="Notes, PDF, Video, Website, Book, Question Bank, Assignment, Previous Year Paper")
    file_link_reference: str
    chapter: Optional[str] = None
    topic: Optional[str] = None
    difficulty: Optional[str] = None
    exam: Optional[str] = None
    status: str = "UNREAD"

class StudyMaterialCreate(StudyMaterialBase):
    pass

class StudyMaterialUpdate(BaseModel):
    subject: Optional[str] = None
    title: Optional[str] = None
    material_type: Optional[str] = None
    file_link_reference: Optional[str] = None
    chapter: Optional[str] = None
    topic: Optional[str] = None
    difficulty: Optional[str] = None
    exam: Optional[str] = None
    status: Optional[str] = None

class StudyMaterialResponse(StudyMaterialBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class StudySessionBase(BaseModel):
    child_id: int
    subject: str
    topic: str
    start_time: datetime
    end_time: datetime
    focus_score: int = Field(..., ge=0, le=100)
    notes: Optional[str] = None

class StudySessionCreate(StudySessionBase):
    pass

class StudySessionResponse(StudySessionBase):
    id: int
    duration_minutes: int

    model_config = ConfigDict(from_attributes=True)


class StudyReportResponse(BaseModel):
    child_id: int
    daily_study_time_minutes: int
    weekly_study_time_minutes: int
    subject_wise_study_time_minutes: Dict[str, int]
    most_studied_subject: Optional[str]
    least_studied_subject: Optional[str]
    study_consistency_percentage: float
    average_focus_score: float
    balance_recommendations: List[str]
