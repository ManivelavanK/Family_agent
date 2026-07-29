from sqlalchemy import Column, Integer, Float, String, Date, Time, Text, ForeignKey, JSON
from app.database.database import Base

class HealthLog(Base):
    __tablename__ = "health_logs"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("child_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    height = Column(Float, nullable=True)  # in cm
    weight = Column(Float, nullable=True)  # in kg
    water_intake_ml = Column(Integer, nullable=False, default=0)
    sleep_hours = Column(Float, nullable=False, default=0.0)
    sleep_time = Column(Time, nullable=True)
    wake_time = Column(Time, nullable=True)
    physical_activity_minutes = Column(Integer, nullable=False, default=0)
    exercise_type = Column(String, nullable=True)
    vaccinations = Column(JSON, nullable=True)  # Store vaccination details list
    health_notes = Column(Text, nullable=True)
