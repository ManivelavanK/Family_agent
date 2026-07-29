from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.settings import HouseholdSettings
from app.schemas.settings import HouseholdSettingsCreate, HouseholdSettingsResponse

router = APIRouter(prefix="/api/v1/settings", tags=["Household Settings"])


@router.get("", response_model=HouseholdSettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    """Fetches the current household settings."""
    settings = db.query(HouseholdSettings).first()
    if not settings:
        # Create a default settings entry if none exists
        settings = HouseholdSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.post("", response_model=HouseholdSettingsResponse)
def update_settings(payload: HouseholdSettingsCreate, db: Session = Depends(get_db)):
    """Updates the household settings parameters."""
    settings = db.query(HouseholdSettings).first()
    if not settings:
        settings = HouseholdSettings()
        db.add(settings)

    settings.family_name = payload.family_name
    settings.primary_contact_phone = payload.primary_contact_phone
    settings.budget_limit_weekly = payload.budget_limit_weekly
    settings.preferred_store = payload.preferred_store
    settings.auto_order_threshold = payload.auto_order_threshold

    db.commit()
    db.refresh(settings)
    return settings
