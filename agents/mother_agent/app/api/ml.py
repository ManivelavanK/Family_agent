from fastapi import APIRouter, HTTPException, status
from app.ml.train_model import train

router = APIRouter(prefix="/api/v1/ml", tags=["ML Training"])


@router.post("/train")
def train_model():
    result = train()
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])
    return result
