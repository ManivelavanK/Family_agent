from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ProfileCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, json_schema_extra={"example": "John Doe"})
    age: int = Field(..., ge=0, json_schema_extra={"example": 75})
    allergies: Optional[str] = Field(None, json_schema_extra={"example": "Peanuts"})
    medical_history: Optional[str] = Field(None, json_schema_extra={"example": "Hypertension, Type 2 Diabetes"})
    emergency_contact_name: str = Field(..., min_length=1, max_length=100, json_schema_extra={"example": "Jane Doe"})
    emergency_contact_phone: str = Field(..., min_length=1, max_length=50, json_schema_extra={"example": "555-0199"})


class ProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, json_schema_extra={"example": "John Doe"})
    age: Optional[int] = Field(None, ge=0, json_schema_extra={"example": 76})
    allergies: Optional[str] = Field(None, json_schema_extra={"example": "None"})
    medical_history: Optional[str] = Field(None, json_schema_extra={"example": "Mild Hypertension"})
    emergency_contact_name: Optional[str] = Field(None, min_length=1, max_length=100, json_schema_extra={"example": "Jane Doe"})
    emergency_contact_phone: Optional[str] = Field(None, min_length=1, max_length=50, json_schema_extra={"example": "555-0199"})


class ProfileResponse(ProfileCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
