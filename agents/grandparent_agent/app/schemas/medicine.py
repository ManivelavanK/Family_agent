from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


class MedicineCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, json_schema_extra={"example": "Metformin"})
    dosage: str = Field(..., min_length=1, max_length=50, json_schema_extra={"example": "500 mg"})
    frequency: str = Field(..., min_length=1, max_length=50, json_schema_extra={"example": "Twice Daily"})
    time_of_day: str = Field(..., min_length=1, max_length=100, json_schema_extra={"example": "Morning"})
    inventory_count: int = Field(0, ge=0, json_schema_extra={"example": 30})

    @field_validator("name", "dosage", "frequency", "time_of_day", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        return v.strip() if isinstance(v, str) else v


class MedicineUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, json_schema_extra={"example": "Metformin"})
    dosage: Optional[str] = Field(None, min_length=1, max_length=50, json_schema_extra={"example": "500 mg"})
    frequency: Optional[str] = Field(None, min_length=1, max_length=50, json_schema_extra={"example": "Twice Daily"})
    time_of_day: Optional[str] = Field(None, min_length=1, max_length=100, json_schema_extra={"example": "Morning"})
    inventory_count: Optional[int] = Field(None, ge=0, json_schema_extra={"example": 40})
    is_active: Optional[bool] = Field(None, json_schema_extra={"example": True})


class MedicineResponse(MedicineCreate):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MedicationIntelligenceResponse(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "Metformin"})
    next_dose: str = Field(..., json_schema_extra={"example": "8 PM"})
    remaining_tablets: int = Field(..., json_schema_extra={"example": 3})
    refill_required: bool = Field(..., json_schema_extra={"example": True})
    missed: bool = Field(..., json_schema_extra={"example": False})
    warning: str = Field(..., json_schema_extra={"example": "Refill required: Only 3 tablets remaining!"})


class MedicationRefillResponse(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "Metformin"})
    remaining_tablets: int = Field(..., json_schema_extra={"example": 3})
    refill_required: bool = Field(..., json_schema_extra={"example": True})

