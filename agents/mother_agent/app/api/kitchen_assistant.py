from fastapi import APIRouter
from app.schemas.voice import VoiceQueryRequest
from app.services.kitchen_assistant import answer_kitchen_query

router = APIRouter(prefix="/api/v1/kitchen-assistant", tags=["AI Kitchen Assistant"])


@router.post("/ask")
def ask_kitchen_assistant(payload: VoiceQueryRequest):
    """Ask culinary prep, food preservation, recipe adjustment, or ingredient substitution queries."""
    answer = answer_kitchen_query(payload.text)
    return {"query": payload.text, "response": answer}
