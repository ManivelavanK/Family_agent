import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.guest import Guest
from app.schemas.guest import GuestCreate, GuestUpdate

logger = logging.getLogger("kinnest.services.guest")

class GuestService:
    @staticmethod
    def create_guest(db: Session, guest_in: GuestCreate) -> Guest:
        db_guest = Guest(
            family_id=guest_in.family_id,
            name=guest_in.name,
            relationship=guest_in.relationship,
            group_name=guest_in.group_name,
            adults=guest_in.adults,
            children=guest_in.children,
            arrival_datetime=guest_in.arrival_datetime,
            departure_datetime=guest_in.departure_datetime,
            accommodation_info=guest_in.accommodation_info,
            food_preferences=guest_in.food_preferences,
            dietary_restrictions=guest_in.dietary_restrictions,
            special_requirements=guest_in.special_requirements,
            transport_info=guest_in.transport_info,
            notes=guest_in.notes
        )
        db.add(db_guest)
        db.commit()
        db.refresh(db_guest)
        logger.info(f"Created guest '{db_guest.name}' (id: {db_guest.id}, family_id: {db_guest.family_id})")
        return db_guest

    @staticmethod
    def get_guest_by_id(db: Session, guest_id: int, family_id: str = "default_family") -> Optional[Guest]:
        return db.query(Guest).filter(Guest.id == guest_id, Guest.family_id == family_id).first()

    @staticmethod
    def get_all_guests(db: Session, family_id: str = "default_family", limit: int = 50) -> List[Guest]:
        return db.query(Guest).filter(Guest.family_id == family_id).order_by(Guest.created_at.desc()).limit(limit).all()

    @staticmethod
    def update_guest(db: Session, guest_id: int, guest_in: GuestUpdate, family_id: str = "default_family") -> Optional[Guest]:
        db_guest = GuestService.get_guest_by_id(db, guest_id, family_id)
        if not db_guest:
            return None

        update_data = guest_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_guest, field, value)

        db.commit()
        db.refresh(db_guest)
        logger.info(f"Updated guest id {guest_id}")
        return db_guest

    @staticmethod
    def delete_guest(db: Session, guest_id: int, family_id: str = "default_family") -> bool:
        db_guest = GuestService.get_guest_by_id(db, guest_id, family_id)
        if not db_guest:
            return False

        db.delete(db_guest)
        db.commit()
        logger.info(f"Deleted guest id {guest_id}")
        return True
