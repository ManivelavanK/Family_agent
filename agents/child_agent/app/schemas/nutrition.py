from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


# --- Nutrition Log Schemas ---

class NutritionLogBase(BaseModel):
    child_id: int
    date: date
    breakfast_eaten: Optional[bool] = Field(default=True, description="Whether breakfast was eaten")
    breakfast_details: Optional[str] = Field(default=None, description="e.g. Oatmeal with berries & milk")
    lunch_eaten: Optional[bool] = Field(default=True, description="Whether lunch was eaten")
    lunch_details: Optional[str] = Field(default=None, description="e.g. Chicken wrap with carrots")
    snack_eaten: Optional[bool] = Field(default=True, description="Whether snacks were eaten")
    snack_details: Optional[str] = Field(default=None, description="e.g. Apple slices & nuts")
    dinner_eaten: Optional[bool] = Field(default=True, description="Whether dinner was eaten")
    dinner_details: Optional[str] = Field(default=None, description="e.g. Grilled salmon & rice")
    water_ml: Optional[int] = Field(default=1500, description="Total water consumed in ml")
    water_glasses: Optional[int] = Field(default=6, description="Total glasses of water consumed")
    meal_notes: Optional[str] = Field(default=None, description="General meal or appetite notes")

class NutritionLogCreate(NutritionLogBase):
    pass

class NutritionLogResponse(NutritionLogBase):
    id: int
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


# --- Analytics & Reminders Schemas ---

class NutritionSummaryResponse(BaseModel):
    child_id: int
    total_days_analyzed: int
    meal_consistency: str
    meal_consistency_score: float
    water_consistency: str
    water_consistency_score: float
    skipped_meals_detected: List[str] = Field(default_factory=list)
    has_skipped_meals: bool
    basic_nutrition_reminders: List[str] = Field(default_factory=list)
    mother_agent_event_recommendations: List[str] = Field(default_factory=list)
    medical_disclaimer: str = Field(
        default="This system provides simple healthy routine recommendations and does NOT make medical or dietary diagnoses."
    )


# --- Mother Agent Integration Bridge Schemas ---

class MotherAgentBridgeEventCreate(BaseModel):
    child_id: int
    date: date
    event_name: str = Field(..., description="e.g. School Sports Event, Marathon, Field Trip")
    child_recommendation: Optional[str] = Field(
        default="Need extra snack/water for tomorrow's sports event.",
        description="Children agent recommendation string"
    )
    mother_agent_grocery_items: Optional[List[str]] = Field(
        default_factory=list,
        description="Suggested grocery items to sync to Mother Agent"
    )

class MotherAgentBridgeEventResponse(MotherAgentBridgeEventCreate):
    id: int
    status: str
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
