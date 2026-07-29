from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.recipe_service import suggest_recipe

router = APIRouter(prefix="/api/v1/recipe", tags=["Recipe Agent"])


@router.get("/suggest")
def recipe(db: Session = Depends(get_db)):
    return suggest_recipe(db)
