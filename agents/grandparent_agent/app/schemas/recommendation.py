from pydantic import BaseModel
from typing import List


class RecommendationItem(BaseModel):
    category: str  # Diet, Fitness, Cognitive, Sleep
    suggestion: str
    rationale: str


class RecommendationResponse(BaseModel):
    summary: str
    recommendations: List[RecommendationItem]
