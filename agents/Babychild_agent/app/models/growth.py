from sqlalchemy import Column, Integer, Float, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database.database import Base

class GrowthRecord(Base):
    __tablename__ = "growth_records"

    id = Column(Integer, primary_key=True, index=True)
    baby_id = Column(Integer, ForeignKey("babies.id", ondelete="CASCADE"), nullable=False, index=True)
    weight_kg = Column(Float, nullable=False)
    height_cm = Column(Float, nullable=False)
    head_circumference_cm = Column(Float, nullable=True)
    record_date = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    baby = relationship("Baby", back_populates="growth_records")
