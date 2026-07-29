from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.shopping_service import generate_shopping_list

router = APIRouter(prefix="/api/v1/shopping", tags=["Shopping Planner"])


@router.get("/list")
def shopping_list(db: Session = Depends(get_db)):
    return generate_shopping_list(db)
