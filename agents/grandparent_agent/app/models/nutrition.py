from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime, timezone
from app.database.database import Base


class Nutrition(Base):
    __tablename__ = "nutrition"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    meal_type = Column(String(50), nullable=False)  # Breakfast, Lunch, Dinner, Snack
    description = Column(Text, nullable=True)
    calories = Column(Integer, default=0, nullable=False)
    water_ml = Column(Integer, default=0, nullable=False)
