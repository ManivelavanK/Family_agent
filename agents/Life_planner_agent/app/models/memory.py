import enum
import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Enum
)
from app.database.session import Base

class MemoryType(str, enum.Enum):
    PREFERENCE = "PREFERENCE"
    PAST_EVENT = "PAST_EVENT"
    PAST_TRIP = "PAST_TRIP"
    PAST_FUNCTION = "PAST_FUNCTION"
    GUEST_PATTERN = "GUEST_PATTERN"
    BUDGET_PATTERN = "BUDGET_PATTERN"
    FOOD_PREFERENCE = "FOOD_PREFERENCE"
    DESTINATION_PREFERENCE = "DESTINATION_PREFERENCE"
    ACTIVITY_PREFERENCE = "ACTIVITY_PREFERENCE"
    FEEDBACK = "FEEDBACK"
    LESSON_LEARNED = "LESSON_LEARNED"
    PLANNING_CORRECTION = "PLANNING_CORRECTION"

class PlannerMemory(Base):
    __tablename__ = "planner_memories"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(String(100), nullable=False, default="default_family", index=True)
    memory_type = Column(Enum(MemoryType), nullable=False, default=MemoryType.PREFERENCE, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    source_type = Column(String(100), nullable=True, default="USER")
    source_id = Column(Integer, nullable=True)
    importance = Column(Integer, nullable=False, default=3)  # 1 (low) to 5 (high)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
