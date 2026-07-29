import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.common import StandardResponse
from app.schemas.routine import FamilyRoutineCreate, FamilyRoutineUpdate, FamilyRoutineResponse
from app.services.routine_service import RoutineService

router = APIRouter(prefix="/routines", tags=["Routines"])

@router.post("", response_model=StandardResponse[FamilyRoutineResponse], status_code=status.HTTP_201_CREATED)
def create_routine(routine_in: FamilyRoutineCreate, db: Session = Depends(get_db)):
    routine = RoutineService.create_routine(db, routine_in)
    return StandardResponse(
        success=True,
        message="Family routine created successfully",
        data=routine
    )

@router.get("", response_model=StandardResponse[List[FamilyRoutineResponse]], status_code=status.HTTP_200_OK)
def get_routines(family_id: str = "default_family", limit: int = 100, db: Session = Depends(get_db)):
    routines = RoutineService.get_all_routines(db, family_id, limit)
    return StandardResponse(
        success=True,
        message="Retrieved family routines successfully",
        data=routines
    )

@router.get("/day/{target_date}", response_model=StandardResponse[List[FamilyRoutineResponse]], status_code=status.HTTP_200_OK)
def get_routines_for_day(target_date: datetime.date, family_id: str = "default_family", db: Session = Depends(get_db)):
    routines = RoutineService.get_routines_for_date(db, target_date, family_id)
    return StandardResponse(
        success=True,
        message=f"Retrieved family routines for {target_date}",
        data=routines
    )

@router.get("/range", response_model=StandardResponse[List[FamilyRoutineResponse]], status_code=status.HTTP_200_OK)
def get_routines_in_range(start_date: datetime.date, end_date: datetime.date, family_id: str = "default_family", db: Session = Depends(get_db)):
    routines = RoutineService.get_routines_in_range(db, start_date, end_date, family_id)
    return StandardResponse(
        success=True,
        message=f"Retrieved routines from {start_date} to {end_date}",
        data=routines
    )

@router.get("/{routine_id}", response_model=StandardResponse[FamilyRoutineResponse], status_code=status.HTTP_200_OK)
def get_routine(routine_id: int, family_id: str = "default_family", db: Session = Depends(get_db)):
    routine = RoutineService.get_routine_by_id(db, routine_id, family_id)
    if not routine:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Routine with ID {routine_id} not found")
    return StandardResponse(
        success=True,
        message="Retrieved routine details",
        data=routine
    )

@router.put("/{routine_id}", response_model=StandardResponse[FamilyRoutineResponse], status_code=status.HTTP_200_OK)
def update_routine(routine_id: int, routine_in: FamilyRoutineUpdate, family_id: str = "default_family", db: Session = Depends(get_db)):
    routine = RoutineService.update_routine(db, routine_id, routine_in, family_id)
    if not routine:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Routine with ID {routine_id} not found")
    return StandardResponse(
        success=True,
        message="Family routine updated successfully",
        data=routine
    )

@router.delete("/{routine_id}", response_model=StandardResponse[dict], status_code=status.HTTP_200_OK)
def delete_routine(routine_id: int, family_id: str = "default_family", db: Session = Depends(get_db)):
    deleted = RoutineService.delete_routine(db, routine_id, family_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Routine with ID {routine_id} not found")
    return StandardResponse(
        success=True,
        message="Family routine deleted successfully",
        data={"deleted_id": routine_id}
    )

@router.post("/check-conflicts", response_model=StandardResponse[List[FamilyRoutineResponse]], status_code=status.HTTP_200_OK)
def check_routine_conflicts(
    member_name: str,
    scheduled_start: datetime.datetime,
    scheduled_end: datetime.datetime,
    family_id: str = "default_family",
    db: Session = Depends(get_db)
):
    conflicts = RoutineService.check_routine_conflicts(db, member_name, scheduled_start, scheduled_end, family_id)
    return StandardResponse(
        success=True,
        message="Checked routine conflicts successfully",
        data=conflicts
    )
