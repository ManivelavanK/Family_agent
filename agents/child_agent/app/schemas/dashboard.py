from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class DailyDashboardResponse(BaseModel):
    greeting: str
    timetable: List[str]
    important_alerts: List[str]
    recommendations: List[str]
    aggregated_data: Dict[str, Any]
