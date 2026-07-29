from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse
from app.services import recommendation_service

router = APIRouter(tags=["Groq AI Intelligence & Recommendations"])


@router.post("/children/recommendation", response_model=RecommendationResponse, status_code=status.HTTP_200_OK)
def get_child_recommendation(
    request: RecommendationRequest, 
    db: Session = Depends(get_db)
):
    """
    Executes the 7-step Groq AI Recommendation Pipeline:
    1. Collect structured DB records for the child.
    2. Compute deterministic summary metrics (financials, attendance, safety status, health).
    3. Obtain Scikit-Learn ML predictions.
    4. Send structured context to Groq AI reasoning engine.
    5. Receive & validate structured response across 10 recommendation categories.
    6. Ensure LLM does NOT calculate or mutate critical values directly.
    7. Return comprehensive structured output.
    """
    try:
        return recommendation_service.generate_recommendation_for_child(db=db, request=request)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Recommendation service error: {str(e)}"
        )
