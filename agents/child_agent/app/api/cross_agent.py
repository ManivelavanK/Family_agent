from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db

from app.schemas.cross_agent import (
    ChildSummaryResponse,
    ChildExpenseCreate,
    ChildExpenseResponse,
    ChildEducationExpenseCreate,
    ChildEducationExpenseResponse,
    FamilyEventsResponse,
    ChildGroceryNeedsResponse,
    ChildCheckInCreate,
    ChildCheckInResponse,
    ChildAlertCreate,
    ChildAlertResponse,
)
from app.services import cross_agent_service

router = APIRouter(prefix="/api/v1/family", tags=["Cross-Agent Integration"])

@router.get("/child-summary/{family_id}", response_model=ChildSummaryResponse)
def get_child_summary(family_id: str, db: Session = Depends(get_db)):
    """
    Retrieves summary profile and activity data for all children in a family.
    """
    return cross_agent_service.get_child_summaries_for_family(db=db, family_id=family_id)

@router.post("/child-expense", response_model=ChildExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_child_expense(expense: ChildExpenseCreate, db: Session = Depends(get_db)):
    """
    Logs an expense made by or for a child.
    """
    return cross_agent_service.create_child_expense(db=db, expense_in=expense)

@router.post("/child-education-expense", response_model=ChildEducationExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_child_education_expense(expense: ChildEducationExpenseCreate, db: Session = Depends(get_db)):
    """
    Logs or proposes an education-related expense (for Father agent synchronization).
    """
    db_exp = cross_agent_service.create_education_expense(db=db, education_expense_in=expense)
    
    # Map from ChildExpense DB model to response schema
    # education expense type is stored in description: "[expense_type] description"
    desc = db_exp.description or ""
    original_desc = desc
    if desc.startswith("[") and "]" in desc:
        original_desc = desc.split("]", 1)[1].strip()

    return ChildEducationExpenseResponse(
        id=db_exp.id,
        family_id=db_exp.family_id,
        child_id=db_exp.child_id,
        amount=db_exp.amount,
        expense_type=expense.expense_type,
        description=original_desc if original_desc else None,
        date=db_exp.date
    )

@router.get("/child-events/{family_id}", response_model=FamilyEventsResponse)
def get_child_events(family_id: str, db: Session = Depends(get_db)):
    """
    Gets events from schedule, exams, holidays, activities for all children in a family.
    """
    return cross_agent_service.get_family_events(db=db, family_id=family_id)

@router.get("/child-grocery-needs/{family_id}", response_model=ChildGroceryNeedsResponse)
def get_child_grocery_needs(family_id: str, db: Session = Depends(get_db)):
    """
    Gets grocery needs recommended by child nutrition / events logs (for Mother agent sync).
    """
    return cross_agent_service.get_grocery_needs(db=db, family_id=family_id)

@router.post("/child-check-in", response_model=ChildCheckInResponse)
def create_child_check_in(check_in: ChildCheckInCreate, db: Session = Depends(get_db)):
    """
    Submits a child's location check-in details.
    """
    db_log = cross_agent_service.create_or_update_check_in(db=db, check_in_in=check_in)
    return ChildCheckInResponse(
        id=db_log.id,
        child_id=db_log.child_id,
        date=db_log.date,
        expected_return_time=db_log.expected_return_time,
        actual_check_in_time=db_log.actual_check_in_time,
        location_note=db_log.location_note,
        status=db_log.status,
        parent_notified=db_log.parent_notified
    )

@router.post("/child-alert", response_model=ChildAlertResponse)
def trigger_child_alert(alert: ChildAlertCreate, db: Session = Depends(get_db)):
    """
    Triggers an emergency/safety alert notification (for Family Dashboard and dashboard notification).
    """
    return cross_agent_service.trigger_child_alert(db=db, alert_in=alert)
