from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey
from app.database.database import Base

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("child_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    activity_type = Column(String, nullable=False)  # Tuition, Sports, Music, Dance, Competition, Club, College project, Study group, Family event, Other
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    location = Column(String, nullable=True)
    priority = Column(String, nullable=False, default="Medium")  # Low, Medium, High
