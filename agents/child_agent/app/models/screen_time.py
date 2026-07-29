from sqlalchemy import Column, Integer, Date, ForeignKey
from app.database.database import Base

class ScreenTimeLog(Base):
    __tablename__ = "screen_time_logs"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("child_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    mobile = Column(Integer, nullable=False, default=0)       # minutes
    gaming = Column(Integer, nullable=False, default=0)       # minutes
    tv = Column(Integer, nullable=False, default=0)           # minutes
    social_media = Column(Integer, nullable=False, default=0) # minutes
    study_screen_time = Column(Integer, nullable=False, default=0) # minutes (educational)
    other = Column(Integer, nullable=False, default=0)        # minutes
    late_night_minutes = Column(Integer, nullable=False, default=0) # minutes used after 10 PM
