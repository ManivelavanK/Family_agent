from sqlalchemy import Column, Integer, String, Date, Time, DateTime, ForeignKey, Text, Boolean
from datetime import datetime
from app.database.database import Base

class ScheduleItem(Base):
    __tablename__ = "schedule_items"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("child_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    day_of_week = Column(String, nullable=False, index=True)  # Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday
    subject = Column(String, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    room = Column(String, nullable=True)
    teacher = Column(String, nullable=True)
    transport_info = Column(String, nullable=True)
    schedule_type = Column(String, nullable=False, default="PERIOD")  # PERIOD, LECTURE, LAB, ASSEMBLY, BUS, CLUB, PROJECT, SCHOOL_ACTIVITY, COMMUTE
    education_stage = Column(String, nullable=True)  # SCHOOL, COLLEGE
    created_at = Column(DateTime, default=datetime.utcnow)


class HolidayCalendar(Base):
    __tablename__ = "holiday_calendars"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("child_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    is_no_school = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
