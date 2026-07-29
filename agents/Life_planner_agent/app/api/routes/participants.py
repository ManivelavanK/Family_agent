from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.common import StandardResponse
from app.schemas.plan import ParticipantCreate, ParticipantUpdate, ParticipantResponse
from app.services.plan_service import ParticipantService, PlanService

router = APIRouter(tags=["Participants"])

@router.post("/plans/{plan_id}/participants", response_model=StandardResponse[ParticipantResponse], status_code=status.HTTP_201_CREATED)
def create_participant(plan_id: int, p_in: ParticipantCreate, db: Session = Depends(get_db)):
    plan = PlanService.get_plan_by_id(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan with ID {plan_id} not found"
        )
    participant = ParticipantService.create_participant(db, plan_id, p_in)
    return StandardResponse(
        success=True,
        message="Participant added successfully",
        data=ParticipantResponse.model_validate(participant)
    )

@router.get("/plans/{plan_id}/participants", response_model=StandardResponse[List[ParticipantResponse]])
def get_participants_by_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = PlanService.get_plan_by_id(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan with ID {plan_id} not found"
        )
    participants = ParticipantService.get_participants_by_plan(db, plan_id)
    return StandardResponse(
        success=True,
        message="Participants retrieved successfully",
        data=[ParticipantResponse.model_validate(p) for p in participants]
    )

@router.delete("/participants/{participant_id}", response_model=StandardResponse[dict])
def delete_participant(participant_id: int, db: Session = Depends(get_db)):
    success = ParticipantService.delete_participant(db, participant_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Participant with ID {participant_id} not found"
        )
    return StandardResponse(
        success=True,
        message="Participant deleted successfully",
        data={"participant_id": participant_id}
    )
