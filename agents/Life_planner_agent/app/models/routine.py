import enum
import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from app.database.session import Base

class RoutinePriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class RoutineStatus(str, enum.Enum):
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"

class FamilyRoutine(Base):
    __tablename__ = "family_routines"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(String(100), nullable=False, default="default_family", index=True)
    member_name = Column(String(100), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    scheduled_start = Column(DateTime(timezone=True), nullable=False, index=True)
    scheduled_end = Column(DateTime(timezone=True), nullable=False, index=True)
    priority = Column(Enum(RoutinePriority), nullable=False, default=RoutinePriority.MEDIUM)
    status = Column(Enum(RoutineStatus), nullable=False, default=RoutineStatus.PLANNED)
    category = Column(String(100), nullable=True, default="GENERAL")
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "family_id": self.family_id,
            "member_name": self.member_name,
            "title": self.title,
            "description": self.description,
            "scheduled_start": str(self.scheduled_start),
            "scheduled_end": str(self.scheduled_end),
            "priority": self.priority.value,
            "status": self.status.value,
            "category": self.category,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at)
        }
