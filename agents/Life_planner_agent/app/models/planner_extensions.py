import enum
import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, Enum, ForeignKey, Date, Boolean
)
from sqlalchemy.orm import relationship as db_relationship
from app.database.session import Base

class GoalCategory(str, enum.Enum):
    PERSONAL = "PERSONAL"
    ACADEMIC = "ACADEMIC"
    FINANCIAL = "FINANCIAL"
    HEALTH = "HEALTH"
    HOUSEHOLD = "HOUSEHOLD"

class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(String(100), nullable=False, default="default_family", index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(Enum(GoalCategory), nullable=False, default=GoalCategory.PERSONAL)
    progress = Column(Float, nullable=False, default=0.0) # Percentage (0-100)
    deadline = Column(Date, nullable=True)
    ai_recommendation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

class HabitCategory(str, enum.Enum):
    WATER = "WATER"
    EXERCISE = "EXERCISE"
    READING = "READING"
    MEDITATION = "MEDITATION"
    STUDY = "STUDY"
    CODING = "CODING"
    CUSTOM = "CUSTOM"

class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(String(100), nullable=False, default="default_family", index=True)
    title = Column(String(255), nullable=False)
    category = Column(Enum(HabitCategory), nullable=False, default=HabitCategory.CUSTOM)
    streak = Column(Integer, nullable=False, default=0)
    max_streak = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    logs = db_relationship("HabitLog", back_populates="habit", cascade="all, delete-orphan")

class HabitLog(Base):
    __tablename__ = "habit_logs"

    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    completed = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    habit = db_relationship("Habit", back_populates="logs")

class DigitalTwin(Base):
    __tablename__ = "digital_twins"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(String(100), unique=True, nullable=False, default="default_family", index=True)
    planning_score = Column(Float, nullable=False, default=80.0)
    routine_consistency = Column(Float, nullable=False, default=75.0)
    goal_completion = Column(Float, nullable=False, default=70.0)
    time_utilization = Column(Float, nullable=False, default=85.0)
    stress_level = Column(Float, nullable=False, default=30.0)
    productivity = Column(Float, nullable=False, default=80.0)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(String(100), nullable=False, default="default_family", index=True)
    title = Column(String(255), nullable=False)
    reminder_datetime = Column(DateTime, nullable=False)
    is_sent = Column(Boolean, nullable=False, default=False)
    event_id = Column(Integer, ForeignKey("calendar_events.id", ondelete="SET NULL"), nullable=True)
    task_id = Column(Integer, ForeignKey("plan_tasks.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
