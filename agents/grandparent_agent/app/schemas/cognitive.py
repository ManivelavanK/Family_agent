from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import List, Optional


class CognitiveJournalCreate(BaseModel):
    entry: str = Field(
        ..., 
        json_schema_extra={"example": "Today I went to the park and met my friend Robert. We talked about our childhood."}
    )
    mood: str = Field(
        ..., 
        json_schema_extra={"example": "Happy"}  # Happy, Neutral, Sad, Anxious
    )


class CognitiveJournalResponse(CognitiveJournalCreate):
    id: int
    date: date
    memory_score: int = Field(..., json_schema_extra={"example": 85})
    created_at: datetime

    class Config:
        from_attributes = True


class CognitiveReportResponse(BaseModel):
    weekly_cognitive_score: float = Field(..., json_schema_extra={"example": 82.5})
    mood_trend: str = Field(..., json_schema_extra={"example": "Mainly Happy"})
    daily_scores: List[dict] = Field(
        ..., 
        json_schema_extra={"example": [{"date": "2026-07-28", "score": 85, "mood": "Happy"}]}
    )
    brain_exercises: List[str] = Field(
        ..., 
        json_schema_extra={"example": ["Word Association Puzzle: Match colors with feelings", "Recall the name of the friend you met at the park"]}
    )
