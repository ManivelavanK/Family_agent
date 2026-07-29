from pydantic import BaseModel, Field
from datetime import date
from typing import Optional


class InsuranceCreate(BaseModel):
    policy_number: str = Field(..., min_length=1, max_length=100, json_schema_extra={"example": "POL-98765432"})
    provider: str = Field(..., min_length=1, max_length=100, json_schema_extra={"example": "Blue Shield Health"})
    coverage_details: Optional[str] = Field(None, json_schema_extra={"example": "Covers inpatient visits, medicines, and diagnostic tests"})
    expiry_date: date = Field(..., json_schema_extra={"example": "2028-12-31"})
    status: str = Field("Active", max_length=50, json_schema_extra={"example": "Active"})


class InsuranceResponse(InsuranceCreate):
    id: int

    class Config:
        from_attributes = True
