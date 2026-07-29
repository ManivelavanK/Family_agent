from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from datetime import datetime, timezone
from app.database.database import Base


class EmergencyIncident(Base):
    __tablename__ = "emergency_incidents"

    id = Column(Integer, primary_key=True, index=True)
    time = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    reason = Column(String(200), nullable=False)
    severity = Column(String(50), default="Critical", nullable=False)
    status = Column(String(50), default="Active", nullable=False)  # Active, Resolved, Dismissed
    family_notified = Column(Boolean, default=False, nullable=False)
    notes = Column(Text, nullable=True)
