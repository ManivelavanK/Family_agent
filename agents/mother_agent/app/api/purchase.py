from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.purchase import PurchaseCreate, PurchaseResponse
from app.services.purchase_service import add_purchase, get_purchase_history

router = APIRouter(prefix="/api/v1/purchase", tags=["Purchase History"])


@router.post("/add", response_model=PurchaseResponse, status_code=status.HTTP_201_CREATED)
def create_purchase(purchase: PurchaseCreate, db: Session = Depends(get_db)):
    return add_purchase(db, purchase)


@router.get("/history", response_model=list[PurchaseResponse])
def history(db: Session = Depends(get_db)):
    return get_purchase_history(db)
