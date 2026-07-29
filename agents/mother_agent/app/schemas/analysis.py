from pydantic import BaseModel


class AnalysisResponse(BaseModel):

    item_name: str

    current_stock: float

    average_daily_usage: float

    estimated_days_remaining: float

    recommendation: str