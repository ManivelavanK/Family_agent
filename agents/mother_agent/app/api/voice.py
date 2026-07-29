from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.voice import VoiceQueryRequest, VoiceQueryResponse
from app.voice.voice_service import process_voice_query

router = APIRouter(prefix="/api/v1/voice", tags=["Voice Assistant"])


@router.post("/query", response_model=VoiceQueryResponse)
def handle_voice_query(payload: VoiceQueryRequest, db: Session = Depends(get_db)):
    """Receives and processes voice command transcriptions."""
    try:
        result = process_voice_query(db, payload.text)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Voice command execution failed: {str(e)}"
        )
