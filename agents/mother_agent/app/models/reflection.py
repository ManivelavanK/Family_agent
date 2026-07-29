from sqlalchemy import Column, Integer, String, DateTime, Index
from datetime import datetime, timezone
from app.database.database import Base


class Reflection(Base):
    __tablename__ = "agent_reflections"

    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String(100), nullable=True, index=True)
    insight = Column(String)
    recommendation = Column(String)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
