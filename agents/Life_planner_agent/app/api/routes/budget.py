from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.common import StandardResponse
from app.schemas.plan import BudgetItemCreate, BudgetItemUpdate, BudgetItemResponse
from app.services.plan_service import BudgetService, PlanService

router = APIRouter(tags=["Budget"])

@router.post("/plans/{plan_id}/budget", response_model=StandardResponse[BudgetItemResponse], status_code=status.HTTP_201_CREATED)
def create_budget_item(plan_id: int, item_in: BudgetItemCreate, db: Session = Depends(get_db)):
    plan = PlanService.get_plan_by_id(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan with ID {plan_id} not found"
        )
    item = BudgetService.create_budget_item(db, plan_id, item_in)
    return StandardResponse(
        success=True,
        message="Budget item created successfully",
        data=BudgetItemResponse.model_validate(item)
    )

@router.get("/plans/{plan_id}/budget", response_model=StandardResponse[List[BudgetItemResponse]])
def get_budget_by_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = PlanService.get_plan_by_id(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan with ID {plan_id} not found"
        )
    items = BudgetService.get_budget_by_plan(db, plan_id)
    return StandardResponse(
        success=True,
        message="Budget items retrieved successfully",
        data=[BudgetItemResponse.model_validate(i) for i in items]
    )

@router.put("/budget/{item_id}", response_model=StandardResponse[BudgetItemResponse])
def update_budget_item(item_id: int, item_in: BudgetItemUpdate, db: Session = Depends(get_db)):
    updated_item = BudgetService.update_budget_item(db, item_id, item_in)
    if not updated_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Budget item with ID {item_id} not found"
        )
    return StandardResponse(
        success=True,
        message="Budget item updated successfully",
        data=BudgetItemResponse.model_validate(updated_item)
    )

@router.delete("/budget/{item_id}", response_model=StandardResponse[dict])
def delete_budget_item(item_id: int, db: Session = Depends(get_db)):
    success = BudgetService.delete_budget_item(db, item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Budget item with ID {item_id} not found"
        )
    return StandardResponse(
        success=True,
        message="Budget item deleted successfully",
        data={"item_id": item_id}
    )
