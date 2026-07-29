from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.price_service import analyze_prices, add_price

router = APIRouter(prefix="/api/v1/price", tags=["Price Tracker Agent"])


class PriceCreate(BaseModel):
    item_name: str = Field(..., max_length=100)
    store_name: str = Field(..., max_length=100)
    price: float = Field(..., gt=0)


@router.post("/add", status_code=status.HTTP_201_CREATED)
def create_price(data: PriceCreate, db: Session = Depends(get_db)):
    return add_price(db, data.item_name, data.store_name, data.price)


@router.get("/compare")
def compare_prices(items: str, db: Session = Depends(get_db)):
    if not items.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="items query param is required.")
    item_list = [i.strip() for i in items.split(",") if i.strip()]
    return analyze_prices(db, item_list)
