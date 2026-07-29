from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


class WeeklyReportResponse(BaseModel):
    id: int
    date: date
    report_json: str = Field(..., json_schema_extra={"example": '{"systolic_avg": 120.5, "sugar_avg": 98.2}'})
    pdf_path: str = Field(..., json_schema_extra={"example": "reports/weekly_report_2026-07-28.pdf"})
    created_at: datetime

    class Config:
        from_attributes = True
