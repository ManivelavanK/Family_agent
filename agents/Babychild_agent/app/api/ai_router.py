from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging

from app.database.database import get_db
from app.services import ai_service, baby_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ai", tags=["AI Assistant"])

class AskQuestionRequest(BaseModel):
    baby_id: int
    family_id: int
    question: str

@router.post("/ask")
def ask_ai_assistant(payload: AskQuestionRequest, db: Session = Depends(get_db)):
    try:
        # Validate baby exists
        baby = baby_service.get_baby_by_id(db=db, baby_id=payload.baby_id)
        if not baby:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Baby with ID {payload.baby_id} not found."
            )
            
        # Validate family ownership
        if baby.family_id != payload.family_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Baby profile does not belong to this family."
            )
            
        answer = ai_service.get_ai_insights(db=db, baby_id=payload.baby_id, question=payload.question)
        return {
            "success": True,
            "message": "AI response generated successfully.",
            "data": {
                "answer": answer
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calling AI Assistant: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating AI response."
        )
