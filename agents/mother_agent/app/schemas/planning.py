from pydantic import BaseModel
from typing import List, Optional


class WeeklyPlanItem(BaseModel):
    item: str
    priority: str
    current_stock: float
    predicted_requirement: float
    recommended_purchase: float
    expiry_risk: bool
    action: str
    reason: List[str]


class PlanningResponse(BaseModel):
    agent: str
    weekly_plan: List[WeeklyPlanItem]
    ai_summary: Optional[str] = None
