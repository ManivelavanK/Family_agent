from fastapi import APIRouter, HTTPException, status
from app.services.forecast_service import forecast

router = APIRouter(prefix="/api/v1/forecast", tags=["Demand Forecasting Agent"])


@router.get("/")
def get_forecast():
    result = forecast()
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=result["error"])
    return result
