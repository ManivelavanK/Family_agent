import logging
from fastapi import APIRouter, Depends, UploadFile, File, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io

from app.database.database import get_db
from app.schemas.voice import VoiceProcessRequest, VoiceSpeakRequest, VoiceTranscribeResponse
from app.schemas.response import APIResponse
from app.voice.speech_to_text import transcribe_audio
from app.voice.text_to_speech import synthesize_speech
from app.voice.voice_service import process_voice_query, run_conversational_chat

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/voice", tags=["Voice Assistant"])


@router.post("/chat", response_model=APIResponse)
def voice_conversational_chat_endpoint(request: VoiceProcessRequest, db: Session = Depends(get_db)):
    """
    Stateful Conversational Chat. Reads latest logs (vitals, sleep, hydration, medicines),
    queries Groq LLM, and returns the natural text response.
    """
    logger.info("Request received: Voice conversational chat: '%s'", request.text)
    chat_result = run_conversational_chat(db, request.text)
    return APIResponse(
        success=True,
        message="Voice conversational chat response generated",
        data=chat_result
    )


@router.post("/chat/audio")
async def voice_conversational_audio_endpoint(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Conversational Voice Audio pipeline. Transcribes uploaded audio, fetches DB parameters,
    queries Groq, synthesizes the text response into voice, and returns a playable MP3 stream.
    """
    logger.info("Request received: Conversational voice chat audio pipeline: %s", file.filename)
    try:
        content = await file.read()
        # 1. Speech to text
        transcription_text = transcribe_audio(content, file.filename)
        
        # 2. Conversational chat answer
        chat_result = run_conversational_chat(db, transcription_text)
        text_response = chat_result["text_response"]
        
        # 3. Text to speech
        audio_bytes = await synthesize_speech(text_response)
        
        # 4. Stream response back
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=chat_response.mp3",
                "X-Transcribed-Text": transcription_text,
                "X-Text-Response": text_response
            }
        )
    except Exception as e:
        logger.exception("Conversational audio pipeline failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Conversational voice pipeline failed: {str(e)}"
        )


@router.post("/transcribe", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def transcribe_audio_endpoint(file: UploadFile = File(...)):
    """
    Transcribe uploaded audio file (wav, mp3, m4a) using Whisper.
    """
    logger.info("Request received: Transcribe voice audio file")
    try:
        content = await file.read()
        transcription_text = transcribe_audio(content, file.filename)
        data = VoiceTranscribeResponse(text=transcription_text)
        return APIResponse(
            success=True,
            message="Audio transcribed successfully",
            data=data.model_dump()
        )
    except Exception as e:
        logger.exception("Failed to transcribe uploaded audio file")
        return APIResponse(
            success=False,
            message=f"Transcription failed: {str(e)}"
        )


@router.post("/process", response_model=APIResponse)
def process_voice_query_endpoint(request: VoiceProcessRequest, db: Session = Depends(get_db)):
    """
    Processes voice transcript query, detects intent, and routes to appropriate service.
    """
    logger.info("Request received: Process text transcript query: '%s'", request.text)
    result = process_voice_query(db, request.text)
    return APIResponse(
        success=True,
        message="Voice query processed successfully",
        data=result
    )


@router.post("/speak")
async def synthesize_speech_endpoint(request: VoiceSpeakRequest):
    """
    Synthesize text response into playable MP3 voice clips.
    """
    logger.info("Request received: Synthesize text response: '%s'", request.text)
    audio_bytes = await synthesize_speech(request.text)
    
    # Return as StreamingResponse
    return StreamingResponse(
        io.BytesIO(audio_bytes),
        media_type="audio/mpeg",
        headers={"Content-Disposition": "inline; filename=speech.mp3"}
    )
