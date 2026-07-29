from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, JSON, Text, Boolean
from datetime import datetime
from app.database.database import Base

class NutritionLog(Base):
    __tablename__ = "nutrition_logs"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("child_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    breakfast_eaten = Column(Boolean, nullable=False, default=True)
    breakfast_details = Column(String, nullable=True)
    lunch_eaten = Column(Boolean, nullable=False, default=True)
    lunch_details = Column(String, nullable=True)
    snack_eaten = Column(Boolean, nullable=False, default=True)
    snack_details = Column(String, nullable=True)
    dinner_eaten = Column(Boolean, nullable=False, default=True)
    dinner_details = Column(String, nullable=True)
    water_ml = Column(Integer, nullable=False, default=1500)
    water_glasses = Column(Integer, nullable=False, default=6)
    meal_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MotherAgentBridgeEvent(Base):
    __tablename__ = "mother_agent_bridge_events"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("child_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    event_name = Column(String, nullable=False)  # e.g., "School Sports Event"
    child_recommendation = Column(Text, nullable=False)  # e.g., "Need extra snack/water."
    mother_agent_grocery_items = Column(JSON, nullable=True)  # List of strings e.g., ["Fruit snacks", "Hydration drink"]
    status = Column(String, nullable=False, default="PENDING_MOTHER_AGENT_SYNC")  # PENDING_MOTHER_AGENT_SYNC, ADDED_TO_GROCERIES
    created_at = Column(DateTime, default=datetime.utcnow)
