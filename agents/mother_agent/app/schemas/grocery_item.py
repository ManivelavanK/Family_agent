from pydantic import BaseModel, Field, field_validator


class GroceryItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., max_length=100)
    quantity: float = Field(..., gt=0)
    unit: str = Field(..., max_length=50)

    @field_validator("name", "unit", "category", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        return v.strip() if isinstance(v, str) else v


class GroceryItemResponse(GroceryItemCreate):
    id: int

    class Config:
        from_attributes = True
