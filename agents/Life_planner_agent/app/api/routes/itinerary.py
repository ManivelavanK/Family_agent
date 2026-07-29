from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.common import StandardResponse
from app.schemas.plan import ItineraryItemCreate, ItineraryItemUpdate, ItineraryItemResponse
from app.services.plan_service import ItineraryService, PlanService

router = APIRouter(tags=["Itinerary"])

@router.post("/plans/{plan_id}/itinerary", response_model=StandardResponse[ItineraryItemResponse], status_code=status.HTTP_201_CREATED)
def create_itinerary_item(plan_id: int, item_in: ItineraryItemCreate, db: Session = Depends(get_db)):
    plan = PlanService.get_plan_by_id(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan with ID {plan_id} not found"
        )
    item = ItineraryService.create_itinerary_item(db, plan_id, item_in)
    return StandardResponse(
        success=True,
        message="Itinerary item created successfully",
        data=ItineraryItemResponse.model_validate(item)
    )

@router.get("/plans/{plan_id}/itinerary", response_model=StandardResponse[List[ItineraryItemResponse]])
def get_itinerary_by_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = PlanService.get_plan_by_id(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan with ID {plan_id} not found"
        )
    items = ItineraryService.get_itinerary_by_plan(db, plan_id)
    return StandardResponse(
        success=True,
        message="Itinerary items retrieved successfully",
        data=[ItineraryItemResponse.model_validate(i) for i in items]
    )

@router.put("/itinerary/{item_id}", response_model=StandardResponse[ItineraryItemResponse])
def update_itinerary_item(item_id: int, item_in: ItineraryItemUpdate, db: Session = Depends(get_db)):
    updated_item = ItineraryService.update_itinerary_item(db, item_id, item_in)
    if not updated_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Itinerary item with ID {item_id} not found"
        )
    return StandardResponse(
        success=True,
        message="Itinerary item updated successfully",
        data=ItineraryItemResponse.model_validate(updated_item)
    )

@router.delete("/itinerary/{item_id}", response_model=StandardResponse[dict])
def delete_itinerary_item(item_id: int, db: Session = Depends(get_db)):
    success = ItineraryService.delete_itinerary_item(db, item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Itinerary item with ID {item_id} not found"
        )
    return StandardResponse(
        success=True,
        message="Itinerary item deleted successfully",
        data={"item_id": item_id}
    )
