from sqlalchemy import Column, Integer, Text, Date, DateTime
from datetime import datetime, timezone
from app.database.database import Base


class DailySummary(Base):
    __tablename__ = "daily_summaries"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, nullable=False, index=True)
    morning_schedule = Column(Text, nullable=True)  # Stores JSON formatted morning schedule
    evening_summary = Column(Text, nullable=True)    # Stores JSON formatted evening summary
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
