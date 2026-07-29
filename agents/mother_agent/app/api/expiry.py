from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.expiry import ExpiryCreate, ExpiryResponse
from app.services.expiry_service import add_expiry, check_expiry

router = APIRouter(prefix="/api/v1/expiry", tags=["Expiry Tracker"])


@router.post("/add", response_model=ExpiryResponse, status_code=status.HTTP_201_CREATED)
def add(expiry: ExpiryCreate, db: Session = Depends(get_db)):
    return add_expiry(db, expiry)


@router.get("/check")
def check(db: Session = Depends(get_db)):
    return check_expiry(db)
