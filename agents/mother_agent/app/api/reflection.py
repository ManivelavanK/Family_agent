from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.reflection_service import generate_reflection, get_reflections

router = APIRouter(prefix="/api/v1/reflection", tags=["Reflection Agent"])


@router.get("/")
def read_reflections(db: Session = Depends(get_db)):
    return get_reflections(db)


@router.post("/{item_name}", status_code=status.HTTP_201_CREATED)
def create_reflection(item_name: str, db: Session = Depends(get_db)):
    result = generate_reflection(db, item_name)
    if isinstance(result, dict) and "message" in result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["message"])
    return result
