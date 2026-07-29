from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, JSON, Text, Boolean
from datetime import datetime
from app.database.database import Base

class DiaryEntry(Base):
    __tablename__ = "diary_entries"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("child_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    mood = Column(String, nullable=True)  # e.g. happy, calm, anxious, sad, angry, stressed
    tags = Column(JSON, nullable=True)     # List of strings e.g. ["school", "friends"]
    share_with_parent = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RelaxationLog(Base):
    __tablename__ = "relaxation_logs"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("child_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    activity_type = Column(String, nullable=False)  # breathing, short walk, music, stretching, meditation, hobby, journaling, screen break, social connection
    duration_minutes = Column(Integer, nullable=True)
    mood_before = Column(String, nullable=True)
    mood_after = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
