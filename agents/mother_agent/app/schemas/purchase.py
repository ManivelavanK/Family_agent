from datetime import date
from pydantic import BaseModel, Field, field_validator


class PurchaseCreate(BaseModel):
    item_name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., max_length=100)
    quantity: float = Field(..., gt=0)
    unit: str = Field(..., max_length=50)
    price: float = Field(..., gt=0)
    purchase_date: date

    @field_validator("item_name", "unit", "category", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        return v.strip() if isinstance(v, str) else v


class PurchaseResponse(PurchaseCreate):
    id: int

    class Config:
        from_attributes = True
