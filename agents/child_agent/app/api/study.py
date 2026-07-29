from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.study import (
    StudyMaterialCreate,
    StudyMaterialUpdate,
    StudyMaterialResponse,
    StudySessionCreate,
    StudySessionResponse,
    StudyReportResponse,
)
from app.services import study_service

router = APIRouter(prefix="/children/study", tags=["Study Tracking & Materials"])


# --- Study Materials Endpoints ---

@router.post("/material", response_model=StudyMaterialResponse, status_code=status.HTTP_201_CREATED)
def create_material(material: StudyMaterialCreate, db: Session = Depends(get_db)):
    return study_service.create_study_material(db=db, material_in=material)


@router.get("/materials/{child_id}", response_model=List[StudyMaterialResponse])
def get_materials(child_id: int, db: Session = Depends(get_db)):
    return study_service.get_materials_by_child_id(db=db, child_id=child_id)


@router.put("/material/{material_id}", response_model=StudyMaterialResponse)
def update_material(material_id: int, material: StudyMaterialUpdate, db: Session = Depends(get_db)):
    db_material = study_service.update_study_material(db=db, material_id=material_id, material_in=material)
    if not db_material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study material with ID {material_id} not found",
        )
    return db_material


@router.delete("/material/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_material(material_id: int, db: Session = Depends(get_db)):
    success = study_service.delete_study_material(db=db, material_id=material_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study material with ID {material_id} not found",
        )
    return None


# --- Study Session Endpoints ---

@router.post("/session", response_model=StudySessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(session: StudySessionCreate, db: Session = Depends(get_db)):
    return study_service.create_study_session(db=db, session_in=session)


@router.get("/sessions/{child_id}", response_model=List[StudySessionResponse])
def get_sessions(child_id: int, db: Session = Depends(get_db)):
    return study_service.get_sessions_by_child_id(db=db, child_id=child_id)


@router.get("/report/{child_id}", response_model=StudyReportResponse)
def get_report(child_id: int, db: Session = Depends(get_db)):
    return study_service.generate_study_report(db=db, child_id=child_id)
