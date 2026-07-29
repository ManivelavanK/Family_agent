from pydantic import BaseModel
from datetime import datetime


class KitchenAlertCreate(BaseModel):
    item_name: str | None = None
    severity: str
    title: str
    description: str
    recommended_action: str


class KitchenAlertResponse(BaseModel):
    id: int
    item_name: str | None
    severity: str
    title: str
    description: str
    recommended_action: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
