from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.pocket_money import (
    PocketMoneyAllowanceCreate,
    PocketMoneyAllowanceResponse,
    ChildExpenseCreate,
    ChildExpenseResponse,
    ExpenseSummaryResponse,
    FinancialEducationResponse,
    SavingGoalCreate,
    SavingGoalResponse,
    SavingAnalysisResponse,
)
from app.services import pocket_money_service

router = APIRouter(tags=["Pocket Money & Expenses"])


@router.post("/children/pocket-money", response_model=PocketMoneyAllowanceResponse, status_code=status.HTTP_201_CREATED)
def allocate_pocket_money(allowance: PocketMoneyAllowanceCreate, db: Session = Depends(get_db)):
    return pocket_money_service.create_allowance(db=db, allowance_in=allowance)


@router.get("/children/pocket-money/{child_id}", response_model=List[PocketMoneyAllowanceResponse])
def get_pocket_money(child_id: int, db: Session = Depends(get_db)):
    return pocket_money_service.get_allowances_by_child_id(db=db, child_id=child_id)


@router.post("/children/expenses", response_model=ChildExpenseResponse, status_code=status.HTTP_201_CREATED)
def record_expense(expense: ChildExpenseCreate, db: Session = Depends(get_db)):
    return pocket_money_service.create_expense(db=db, expense_in=expense)


@router.get("/children/expenses/{child_id}", response_model=List[ChildExpenseResponse])
def get_expenses(child_id: int, db: Session = Depends(get_db)):
    return pocket_money_service.get_expenses_by_child_id(db=db, child_id=child_id)


@router.get("/children/expenses/{child_id}/summary", response_model=ExpenseSummaryResponse)
def get_expense_summary(child_id: int, db: Session = Depends(get_db)):
    return pocket_money_service.generate_expense_summary(db=db, child_id=child_id)


@router.get("/children/expenses/{child_id}/budget", response_model=FinancialEducationResponse)
def get_budget_advice(child_id: int, db: Session = Depends(get_db)):
    advice = pocket_money_service.get_financial_education_tips(db=db, child_id=child_id)
    if not advice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child profile with ID {child_id} not found to generate budgeting advice",
        )
    return advice


@router.get("/children/expenses/{child_id}/saving-analysis", response_model=SavingAnalysisResponse)
def get_saving_analysis(child_id: int, db: Session = Depends(get_db)):
    return pocket_money_service.get_saving_goals_analysis(db=db, child_id=child_id)


# Goal creation endpoint to make saving-analysis work
@router.post("/children/expenses/saving-goal", response_model=SavingGoalResponse, status_code=status.HTTP_201_CREATED)
def create_saving_goal(goal: SavingGoalCreate, db: Session = Depends(get_db)):
    return pocket_money_service.create_saving_goal(db=db, goal_in=goal)


# Stub integration with Father Agent
@router.post("/children/expenses/{child_id}/request-funding", status_code=status.HTTP_202_ACCEPTED)
def request_parental_funding(child_id: int, amount: float, purpose: str, db: Session = Depends(get_db)):
    return pocket_money_service.request_parental_funding_interface(db=db, child_id=child_id, amount=amount, purpose=purpose)
