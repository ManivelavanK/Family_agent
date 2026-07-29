from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database.database import Base

class Feeding(Base):
    __tablename__ = "feedings"

    id = Column(Integer, primary_key=True, index=True)
    baby_id = Column(Integer, ForeignKey("babies.id", ondelete="CASCADE"), nullable=False, index=True)
    feeding_type = Column(String(50), nullable=False)
    food_name = Column(String(100), nullable=True)
    quantity_ml = Column(Float, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    feeding_time = Column(DateTime, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    baby = relationship("Baby", back_populates="feedings")
