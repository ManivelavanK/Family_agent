from sqlalchemy import Column, Integer, Float, String, Date
from app.database.database import Base


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, unique=True)
    steps = Column(Integer, default=0, nullable=False)
    sleep_hours = Column(Float, default=0.0, nullable=False)
    activity_type = Column(String(100), nullable=True)  # Walking, Yoga, etc.
    duration_minutes = Column(Integer, default=0, nullable=False)
