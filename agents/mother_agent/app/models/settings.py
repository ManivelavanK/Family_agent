from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime, timezone
from app.database.database import Base


class HouseholdSettings(Base):
    __tablename__ = "household_settings"

    id = Column(Integer, primary_key=True, index=True)
    family_name = Column(String(100), default="Family", nullable=False)
    primary_contact_phone = Column(String(50), default="whatsapp:+910000000000", nullable=False)
    budget_limit_weekly = Column(Float, default=150.0, nullable=False)
    preferred_store = Column(String(100), default="Local Supermarket")
    auto_order_threshold = Column(Float, default=2.0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
