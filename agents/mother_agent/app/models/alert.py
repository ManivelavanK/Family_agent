from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from app.database.database import Base


class KitchenAlert(Base):
    __tablename__ = "kitchen_alerts"

    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String(100), nullable=True)
    severity = Column(String(50), nullable=False)  # High, Medium, Low
    title = Column(String(200), nullable=False)
    description = Column(String(500), nullable=False)
    recommended_action = Column(String(500), nullable=False)
    status = Column(String(50), default="Active", nullable=False)  # Active, Resolved
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
