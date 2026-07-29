from sqlalchemy import Column, Integer, String, Text, Date, DateTime
from datetime import datetime, timezone, date
from app.database.database import Base


class CognitiveLog(Base):
    __tablename__ = "cognitive_logs"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, default=lambda: date.today(), nullable=False, index=True)
    journal_entry = Column(Text, nullable=False)
    mood = Column(String(50), nullable=False)  # Happy, Neutral, Sad, Anxious
    memory_score = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
