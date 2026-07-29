from pydantic import BaseModel
from datetime import datetime


class HouseholdSettingsBase(BaseModel):
    family_name: str
    primary_contact_phone: str
    budget_limit_weekly: float
    preferred_store: str | None = None
    auto_order_threshold: float = 2.0


class HouseholdSettingsCreate(HouseholdSettingsBase):
    pass


class HouseholdSettingsResponse(HouseholdSettingsBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
