import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

class GuestBase(BaseModel):
    family_id: str = Field("default_family", max_length=100)
    name: str = Field(..., max_length=255)
    relationship: Optional[str] = Field(None, max_length=100)
    group_name: Optional[str] = Field(None, max_length=100)
    adults: int = Field(1, ge=1)
    children: int = Field(0, ge=0)
    arrival_datetime: Optional[datetime.datetime] = None
    departure_datetime: Optional[datetime.datetime] = None
    accommodation_info: Optional[str] = None
    food_preferences: Optional[str] = None
    dietary_restrictions: Optional[str] = None
    special_requirements: Optional[str] = None
    transport_info: Optional[str] = None
    notes: Optional[str] = None

class GuestCreate(GuestBase):
    pass

class GuestUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    relationship: Optional[str] = Field(None, max_length=100)
    group_name: Optional[str] = Field(None, max_length=100)
    adults: Optional[int] = Field(None, ge=1)
    children: Optional[int] = Field(None, ge=0)
    arrival_datetime: Optional[datetime.datetime] = None
    departure_datetime: Optional[datetime.datetime] = None
    accommodation_info: Optional[str] = None
    food_preferences: Optional[str] = None
    dietary_restrictions: Optional[str] = None
    special_requirements: Optional[str] = None
    transport_info: Optional[str] = None
    notes: Optional[str] = None

class GuestResponse(GuestBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
