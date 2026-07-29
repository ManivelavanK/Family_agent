from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.database import get_db
from app.schemas.grocery_item import GroceryItemCreate, GroceryItemResponse
from app.services.inventory_service import add_item, get_items
from app.models.grocery_item import GroceryItem

router = APIRouter(prefix="/api/v1/inventory", tags=["Inventory"])


@router.post("/add", status_code=status.HTTP_201_CREATED)
def create_item(item: GroceryItemCreate, db: Session = Depends(get_db)):
    return add_item(db, item)


@router.get("/")
def list_items(db: Session = Depends(get_db)):
    return get_items(db)


@router.delete("/{item_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_name: str, db: Session = Depends(get_db)):
    item = (
        db.query(GroceryItem)
        .filter(func.lower(GroceryItem.name) == item_name.lower())
        .first()
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item '{item_name}' not found.",
        )
    db.delete(item)
    db.commit()
