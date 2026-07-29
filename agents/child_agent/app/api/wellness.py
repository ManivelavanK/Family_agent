from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.wellness import (
    DiaryEntryCreate,
    DiaryEntryUpdate,
    DiaryEntryResponse,
    RelaxationResponse,
    RelaxationLogCreate,
    RelaxationLogResponse,
)
from app.services import wellness_service

router = APIRouter(tags=["Personal Diary & Relaxation Agent"])


# --- Diary APIs ---

@router.post("/children/diary", response_model=DiaryEntryResponse, status_code=status.HTTP_201_CREATED)
def create_diary_entry(entry: DiaryEntryCreate, db: Session = Depends(get_db)):
    return wellness_service.create_diary_entry(db=db, entry_in=entry)


@router.get("/children/diary/{child_id}", response_model=List[DiaryEntryResponse])
def get_child_diary_entries(
    child_id: int, 
    requester_role: Optional[str] = Query("child", description="child or parent"), 
    db: Session = Depends(get_db)
):
    entries = wellness_service.get_child_diary_entries(db=db, child_id=child_id)
    if requester_role and requester_role.lower() == "parent":
        # Privacy enforcement: Do not expose unshared diary content to parents automatically
        entries = [e for e in entries if e.share_with_parent is True]
    return entries


@router.get("/children/diary/{child_id}/{entry_id}", response_model=DiaryEntryResponse)
def get_diary_entry(
    child_id: int, 
    entry_id: int, 
    requester_role: Optional[str] = Query("child", description="child or parent"), 
    db: Session = Depends(get_db)
):
    entry = wellness_service.get_diary_entry_by_id(db=db, child_id=child_id, entry_id=entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Diary entry ID {entry_id} not found for child ID {child_id}"
        )
    if requester_role and requester_role.lower() == "parent" and not entry.share_with_parent:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Privacy Notice: This personal diary entry is private to the child."
        )
    return entry


@router.put("/children/diary/{entry_id}", response_model=DiaryEntryResponse)
def update_diary_entry(entry_id: int, update_in: DiaryEntryUpdate, db: Session = Depends(get_db)):
    updated = wellness_service.update_diary_entry(db=db, entry_id=entry_id, update_in=update_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Diary entry ID {entry_id} not found"
        )
    return updated


@router.delete("/children/diary/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_diary_entry(entry_id: int, db: Session = Depends(get_db)):
    success = wellness_service.delete_diary_entry(db=db, entry_id=entry_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Diary entry ID {entry_id} not found"
        )
    return None


# --- Relaxation & Wellbeing APIs ---

@router.get("/children/wellness/{child_id}/relaxation", response_model=RelaxationResponse)
def get_relaxation_suggestions(child_id: int, db: Session = Depends(get_db)):
    return wellness_service.generate_relaxation_suggestions(db=db, child_id=child_id)


@router.post("/children/wellness/relaxation/log", response_model=RelaxationLogResponse, status_code=status.HTTP_201_CREATED)
def log_relaxation_activity(log: RelaxationLogCreate, db: Session = Depends(get_db)):
    return wellness_service.create_relaxation_log(db=db, log_in=log)
