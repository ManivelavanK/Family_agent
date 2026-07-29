from datetime import date
from pydantic import BaseModel
from typing import Optional


class ExpiryCreate(BaseModel):
    item_name: str
    expiry_date: date


class ExpiryResponse(BaseModel):
    id: int
    item_name: str
    expiry_date: date

    class Config:
        from_attributes = True


class ExpiryCheckItem(BaseModel):
    item: str
    expiry_date: str
    days_remaining: int
    status: str
