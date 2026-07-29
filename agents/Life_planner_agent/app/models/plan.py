import enum
import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, Enum, ForeignKey, Date, Time
)
from sqlalchemy.orm import relationship as db_relationship
from app.database.session import Base

class PlanType(str, enum.Enum):
    EVENT = "EVENT"
    FUNCTION = "FUNCTION"
    TRAVEL = "TRAVEL"

class PlanStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PLANNING = "PLANNING"
    READY = "READY"
    APPROVED = "APPROVED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class TaskPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"

class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class BudgetStatus(str, enum.Enum):
    ESTIMATED = "ESTIMATED"
    PLANNED = "PLANNED"
    PAID = "PAID"

class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    plan_type = Column(Enum(PlanType), nullable=False, default=PlanType.EVENT)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    number_of_people = Column(Integer, nullable=False, default=1)
    budget = Column(Float, nullable=False, default=0.0)
    status = Column(Enum(PlanStatus), nullable=False, default=PlanStatus.DRAFT)
    location = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    tasks = db_relationship("PlanTask", back_populates="plan", cascade="all, delete-orphan")
    budget_items = db_relationship("BudgetItem", back_populates="plan", cascade="all, delete-orphan")
    itinerary_items = db_relationship("ItineraryItem", back_populates="plan", cascade="all, delete-orphan")
    participants = db_relationship("Participant", back_populates="plan", cascade="all, delete-orphan")

class PlanTask(Base):
    __tablename__ = "plan_tasks"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(Date, nullable=True)
    priority = Column(Enum(TaskPriority), nullable=False, default=TaskPriority.MEDIUM)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.PENDING)
    estimated_cost = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    plan = db_relationship("Plan", back_populates="tasks")

class BudgetItem(Base):
    __tablename__ = "budget_items"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    estimated_amount = Column(Float, nullable=False, default=0.0)
    actual_amount = Column(Float, nullable=False, default=0.0)
    status = Column(Enum(BudgetStatus), nullable=False, default=BudgetStatus.ESTIMATED)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    plan = db_relationship("Plan", back_populates="budget_items")

class ItineraryItem(Base):
    __tablename__ = "itinerary_items"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    activity = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    estimated_cost = Column(Float, nullable=False, default=0.0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    plan = db_relationship("Plan", back_populates="itinerary_items")

class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=True)
    relationship = Column(String(100), nullable=True)
    special_requirements = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    plan = db_relationship("Plan", back_populates="participants")
