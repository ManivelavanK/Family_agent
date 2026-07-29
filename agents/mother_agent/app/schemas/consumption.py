from datetime import date
from pydantic import BaseModel, Field, field_validator


class ConsumptionCreate(BaseModel):
    item_name: str = Field(..., min_length=1, max_length=100)
    quantity_used: float = Field(..., gt=0)
    unit: str = Field(..., max_length=50)
    consumption_date: date

    @field_validator("item_name", "unit", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        return v.strip() if isinstance(v, str) else v


class ConsumptionResponse(ConsumptionCreate):
    id: int

    class Config:
        from_attributes = True
