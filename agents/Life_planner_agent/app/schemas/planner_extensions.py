import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.planner_extensions import GoalCategory, HabitCategory

# Goal Schemas
class GoalBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    category: GoalCategory = GoalCategory.PERSONAL
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    deadline: Optional[datetime.date] = None
    ai_recommendation: Optional[str] = None

class GoalCreate(GoalBase):
    family_id: str = "default_family"

class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[GoalCategory] = None
    progress: Optional[float] = Field(None, ge=0.0, le=100.0)
    deadline: Optional[datetime.date] = None
    ai_recommendation: Optional[str] = None

class GoalResponse(GoalBase):
    id: int
    family_id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

# Habit Log Schemas
class HabitLogBase(BaseModel):
    date: datetime.date
    completed: bool = False

class HabitLogCreate(HabitLogBase):
    pass

class HabitLogResponse(HabitLogBase):
    id: int
    habit_id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# Habit Schemas
class HabitBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    category: HabitCategory = HabitCategory.CUSTOM
    streak: int = 0
    max_streak: int = 0

class HabitCreate(HabitBase):
    family_id: str = "default_family"

class HabitUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[HabitCategory] = None
    streak: Optional[int] = None
    max_streak: Optional[int] = None

class HabitResponse(HabitBase):
    id: int
    family_id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    logs: List[HabitLogResponse] = []

    class Config:
        from_attributes = True

# Digital Twin Schemas
class DigitalTwinBase(BaseModel):
    planning_score: float = Field(default=80.0, ge=0.0, le=100.0)
    routine_consistency: float = Field(default=75.0, ge=0.0, le=100.0)
    goal_completion: float = Field(default=70.0, ge=0.0, le=100.0)
    time_utilization: float = Field(default=85.0, ge=0.0, le=100.0)
    stress_level: float = Field(default=30.0, ge=0.0, le=100.0)
    productivity: float = Field(default=80.0, ge=0.0, le=100.0)

class DigitalTwinCreate(DigitalTwinBase):
    family_id: str = "default_family"

class DigitalTwinUpdate(BaseModel):
    planning_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    routine_consistency: Optional[float] = Field(None, ge=0.0, le=100.0)
    goal_completion: Optional[float] = Field(None, ge=0.0, le=100.0)
    time_utilization: Optional[float] = Field(None, ge=0.0, le=100.0)
    stress_level: Optional[float] = Field(None, ge=0.0, le=100.0)
    productivity: Optional[float] = Field(None, ge=0.0, le=100.0)

class DigitalTwinResponse(DigitalTwinBase):
    id: int
    family_id: str
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

# Reminder Schemas
class ReminderBase(BaseModel):
    title: str
    reminder_datetime: datetime.datetime
    is_sent: bool = False
    event_id: Optional[int] = None
    task_id: Optional[int] = None

class ReminderCreate(ReminderBase):
    family_id: str = "default_family"

class ReminderUpdate(BaseModel):
    title: Optional[str] = None
    reminder_datetime: Optional[datetime.datetime] = None
    is_sent: Optional[bool] = None
    event_id: Optional[int] = None
    task_id: Optional[int] = None

class ReminderResponse(ReminderBase):
    id: int
    family_id: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True
