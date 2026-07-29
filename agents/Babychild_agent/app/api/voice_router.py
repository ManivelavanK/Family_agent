from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
import logging

from app.database.database import get_db
from app.services import voice_service, baby_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/voice", tags=["Voice Assistant"])

@router.post("/query")
async def voice_query(
    baby_id: int = Form(...),
    family_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # Validate baby exists
        baby = baby_service.get_baby_by_id(db=db, baby_id=baby_id)
        if not baby:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Baby with ID {baby_id} not found."
            )
            
        # Validate family ownership
        if baby.family_id != family_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Baby profile does not belong to this family."
            )
            
        audio_bytes = await file.read()
        result = await voice_service.process_voice_query(
            db=db,
            baby_id=baby_id,
            audio_bytes=audio_bytes,
            filename=file.filename
        )
        
        return {
            "success": True,
            "message": "AI voice query processed successfully.",
            "data": {
                "recognized_text": result["recognized_text"],
                "answer": result["ai_answer"],
                "audio_file_path": result["audio_file_path"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing voice query for baby {baby_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the voice query."
        )
