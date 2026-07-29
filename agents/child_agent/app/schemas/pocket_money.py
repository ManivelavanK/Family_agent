from datetime import date
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict

# Allowance
class PocketMoneyAllowanceBase(BaseModel):
    family_id: str
    child_id: int
    amount: float = Field(..., ge=0.0)
    frequency: str = Field(..., description="Daily, Weekly, Monthly")
    date: date

class PocketMoneyAllowanceCreate(PocketMoneyAllowanceBase):
    pass

class PocketMoneyAllowanceResponse(PocketMoneyAllowanceBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# Expense
class ChildExpenseBase(BaseModel):
    family_id: str
    child_id: int
    amount: float = Field(..., ge=0.0)
    category: str = Field(..., description="Food, Transport, Education, Entertainment, Shopping, Gaming, Subscriptions, Friends, Emergency, Other")
    description: Optional[str] = None
    date: date

class ChildExpenseCreate(ChildExpenseBase):
    pass

class ChildExpenseResponse(ChildExpenseBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# Saving Goal
class SavingGoalBase(BaseModel):
    child_id: int
    title: str
    target_amount: float = Field(..., ge=0.0)
    current_saved: float = Field(0.0, ge=0.0)
    target_date: date

class SavingGoalCreate(SavingGoalBase):
    pass

class SavingGoalResponse(SavingGoalBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# Reports & Summaries
class ExpenseSummaryResponse(BaseModel):
    total_allowance: float
    total_spent: float
    remaining_allowance: float
    spending_by_category: Dict[str, float]
    saving_percentage: float
    average_daily_spending: float
    projected_month_end_spending: float

class FinancialEducationResponse(BaseModel):
    age_group: str
    tips: List[str]
    recommended_budget_split: Dict[str, float]

class SavingAnalysisResponse(BaseModel):
    total_goals: int
    goals_progress: List[Dict[str, Any]] = Field(default_factory=list)
