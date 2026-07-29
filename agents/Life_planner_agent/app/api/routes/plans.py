from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.common import StandardResponse
from app.schemas.plan import PlanCreate, PlanUpdate, PlanResponse
from app.services.plan_service import PlanService

router = APIRouter(prefix="/plans", tags=["Plans"])

@router.post("", response_model=StandardResponse[PlanResponse], status_code=status.HTTP_201_CREATED)
def create_plan(plan_in: PlanCreate, db: Session = Depends(get_db)):
    plan = PlanService.create_plan(db, plan_in)
    return StandardResponse(
        success=True,
        message="Plan created successfully",
        data=PlanResponse.model_validate(plan)
    )

@router.get("", response_model=StandardResponse[List[PlanResponse]])
def get_plans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    plans = PlanService.get_all_plans(db, skip=skip, limit=limit)
    return StandardResponse(
        success=True,
        message="Plans retrieved successfully",
        data=[PlanResponse.model_validate(p) for p in plans]
    )

@router.get("/{plan_id}", response_model=StandardResponse[PlanResponse])
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = PlanService.get_plan_by_id(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan with ID {plan_id} not found"
        )
    return StandardResponse(
        success=True,
        message="Plan retrieved successfully",
        data=PlanResponse.model_validate(plan)
    )

@router.put("/{plan_id}", response_model=StandardResponse[PlanResponse])
def update_plan(plan_id: int, plan_in: PlanUpdate, db: Session = Depends(get_db)):
    updated_plan = PlanService.update_plan(db, plan_id, plan_in)
    if not updated_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan with ID {plan_id} not found"
        )
    return StandardResponse(
        success=True,
        message="Plan updated successfully",
        data=PlanResponse.model_validate(updated_plan)
    )

@router.delete("/{plan_id}", response_model=StandardResponse[dict])
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    success = PlanService.delete_plan(db, plan_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan with ID {plan_id} not found"
        )
    return StandardResponse(
        success=True,
        message="Plan deleted successfully",
        data={"plan_id": plan_id}
    )
