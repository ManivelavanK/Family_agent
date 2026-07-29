from fastapi import APIRouter
from app.schemas.common import StandardResponse

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=StandardResponse[dict])
def health_check():
    return StandardResponse(
        success=True,
        message="KinNest Life Planner Agent is running",
        data={"status": "healthy"}
    )
