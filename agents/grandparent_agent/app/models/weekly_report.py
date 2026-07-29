from sqlalchemy import Column, Integer, String, Text, Date, DateTime
from datetime import datetime, timezone
from app.database.database import Base


class WeeklyReport(Base):
    __tablename__ = "weekly_reports"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, nullable=False, index=True)  # Ending date (Sunday) of the week
    report_json = Column(Text, nullable=False)                  # Stores the JSON data of weekly averages
    pdf_path = Column(String(500), nullable=False)               # Path to PDF file on disk
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
