from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.common import StandardResponse
from app.schemas.guest import GuestCreate, GuestUpdate, GuestResponse
from app.services.guest_service import GuestService

router = APIRouter(prefix="/guests", tags=["Guests"])

@router.post("", response_model=StandardResponse[GuestResponse], status_code=status.HTTP_201_CREATED)
def create_guest(guest_in: GuestCreate, db: Session = Depends(get_db)):
    guest = GuestService.create_guest(db, guest_in)
    return StandardResponse(
        success=True,
        message="Guest created successfully",
        data=guest
    )

@router.get("", response_model=StandardResponse[List[GuestResponse]], status_code=status.HTTP_200_OK)
def get_guests(family_id: str = "default_family", limit: int = 50, db: Session = Depends(get_db)):
    guests = GuestService.get_all_guests(db, family_id, limit)
    return StandardResponse(
        success=True,
        message="Retrieved guests successfully",
        data=guests
    )

@router.get("/{guest_id}", response_model=StandardResponse[GuestResponse], status_code=status.HTTP_200_OK)
def get_guest(guest_id: int, family_id: str = "default_family", db: Session = Depends(get_db)):
    guest = GuestService.get_guest_by_id(db, guest_id, family_id)
    if not guest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Guest with ID {guest_id} not found")
    return StandardResponse(
        success=True,
        message="Retrieved guest details",
        data=guest
    )

@router.put("/{guest_id}", response_model=StandardResponse[GuestResponse], status_code=status.HTTP_200_OK)
def update_guest(guest_id: int, guest_in: GuestUpdate, family_id: str = "default_family", db: Session = Depends(get_db)):
    guest = GuestService.update_guest(db, guest_id, guest_in, family_id)
    if not guest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Guest with ID {guest_id} not found")
    return StandardResponse(
        success=True,
        message="Guest updated successfully",
        data=guest
    )

@router.delete("/{guest_id}", response_model=StandardResponse[dict], status_code=status.HTTP_200_OK)
def delete_guest(guest_id: int, family_id: str = "default_family", db: Session = Depends(get_db)):
    deleted = GuestService.delete_guest(db, guest_id, family_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Guest with ID {guest_id} not found")
    return StandardResponse(
        success=True,
        message="Guest deleted successfully",
        data={"deleted_id": guest_id}
    )
