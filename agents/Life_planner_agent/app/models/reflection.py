import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship as db_relationship
from app.database.session import Base

class PlanReflection(Base):
    __tablename__ = "plan_reflections"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Integer, nullable=False, default=5)  # 1 to 5
    what_went_well = Column(Text, nullable=True)
    what_went_wrong = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)
    future_suggestions = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    plan = db_relationship("Plan", backref="reflections")
