from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class NutritionCreate(BaseModel):
    meal_type: str = Field(..., min_length=1, max_length=50, json_schema_extra={"example": "Breakfast"})
    description: Optional[str] = Field(None, json_schema_extra={"example": "Oatmeal with bananas and a glass of milk"})
    calories: int = Field(0, ge=0, json_schema_extra={"example": 350})
    water_ml: int = Field(0, ge=0, json_schema_extra={"example": 250})


class NutritionResponse(NutritionCreate):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
