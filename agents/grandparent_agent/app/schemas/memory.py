from pydantic import BaseModel, Field
from typing import List


class MemoryLogCreate(BaseModel):
    entry: str = Field(
        ..., 
        description="The daily reflection or journal entry of the grandparent.",
        json_schema_extra={"example": "Today I visited the temple and walked for 15 minutes."}
    )


class QuizQuestion(BaseModel):
    question: str = Field(..., json_schema_extra={"example": "What is the capital of France?"})
    options: List[str] = Field(..., json_schema_extra={"example": ["Paris", "London", "Berlin", "Madrid"]})
    correct_answer: str = Field(..., json_schema_extra={"example": "Paris"})


class CognitiveQuizResponse(BaseModel):
    quiz_title: str = Field(..., json_schema_extra={"example": "Daily Memory Challenge"})
    questions: List[QuizQuestion]
