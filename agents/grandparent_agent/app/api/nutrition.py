import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.nutrition import Nutrition
from app.schemas.nutrition import NutritionCreate, NutritionResponse
from app.schemas.response import APIResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/nutrition", tags=["Nutrition"])


@router.post("/add", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def create_nutrition_log(nut_in: NutritionCreate, db: Session = Depends(get_db)):
    logger.info("Request received: Add nutrition log")
    db_nut = Nutrition(
        meal_type=nut_in.meal_type,
        description=nut_in.description,
        calories=nut_in.calories,
        water_ml=nut_in.water_ml
    )
    db.add(db_nut)
    db.commit()
    db.refresh(db_nut)
    logger.info("Database updated: Nutrition entry created")
    return APIResponse(
        success=True,
        message="Nutrition logged successfully",
        data=NutritionResponse.model_validate(db_nut)
    )


@router.get("/", response_model=APIResponse)
def list_nutrition_logs(limit: int = 50, db: Session = Depends(get_db)):
    logger.info("Request received: List nutrition logs")
    logs = db.query(Nutrition).order_by(Nutrition.timestamp.desc()).limit(limit).all()
    data = [NutritionResponse.model_validate(log) for log in logs]
    return APIResponse(
        success=True,
        message="Nutrition logs retrieved successfully",
        data=data
    )


@router.put("/{nut_id}", response_model=APIResponse)
def modify_nutrition(nut_id: int, nut_in: NutritionCreate, db: Session = Depends(get_db)):
    logger.info("Request received: Update nutrition ID %d", nut_id)
    existing = db.query(Nutrition).filter(Nutrition.id == nut_id).first()
    if not existing:
        logger.warning("Nutrition update failed: Nutrition not found")
        return APIResponse(
            success=False,
            message="Nutrition record not found"
        )
    existing.meal_type = nut_in.meal_type
    existing.description = nut_in.description
    existing.calories = nut_in.calories
    existing.water_ml = nut_in.water_ml
    db.commit()
    db.refresh(existing)
    logger.info("Database updated: Nutrition ID %d modified", nut_id)
    return APIResponse(
        success=True,
        message="Nutrition updated successfully",
        data=NutritionResponse.model_validate(existing)
    )


@router.delete("/{nut_id}", response_model=APIResponse)
def remove_nutrition(nut_id: int, db: Session = Depends(get_db)):
    logger.info("Request received: Delete nutrition ID %d", nut_id)
    existing = db.query(Nutrition).filter(Nutrition.id == nut_id).first()
    if not existing:
        logger.warning("Nutrition deletion failed: Nutrition not found")
        return APIResponse(
            success=False,
            message="Nutrition record not found"
        )
    db.delete(existing)
    db.commit()
    logger.info("Database updated: Nutrition ID %d deleted", nut_id)
    return APIResponse(
        success=True,
        message="Nutrition record deleted successfully"
    )
