import datetime
import calendar
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any

from app.models.pocket_money import PocketMoneyAllowance, ChildExpense, SavingGoal
from app.models.profile import ChildProfile
from app.schemas.pocket_money import (
    PocketMoneyAllowanceCreate,
    ChildExpenseCreate,
    SavingGoalCreate,
    ExpenseSummaryResponse,
    FinancialEducationResponse,
    SavingAnalysisResponse,
)
from app.services.age_adaptation_service import classify_age_group

# --- Allowance CRUD ---

def create_allowance(db: Session, allowance_in: PocketMoneyAllowanceCreate) -> PocketMoneyAllowance:
    db_allowance = PocketMoneyAllowance(
        family_id=allowance_in.family_id,
        child_id=allowance_in.child_id,
        amount=allowance_in.amount,
        frequency=allowance_in.frequency,
        date=allowance_in.date,
    )
    db.add(db_allowance)
    db.commit()
    db.refresh(db_allowance)
    return db_allowance

def get_allowances_by_child_id(db: Session, child_id: int) -> List[PocketMoneyAllowance]:
    return db.query(PocketMoneyAllowance).filter(PocketMoneyAllowance.child_id == child_id).order_by(PocketMoneyAllowance.date.desc()).all()


# --- Expense CRUD ---

def create_expense(db: Session, expense_in: ChildExpenseCreate) -> ChildExpense:
    db_expense = ChildExpense(
        family_id=expense_in.family_id,
        child_id=expense_in.child_id,
        amount=expense_in.amount,
        category=expense_in.category.capitalize(),  # Normalize category casing
        description=expense_in.description,
        date=expense_in.date,
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

def get_expenses_by_child_id(db: Session, child_id: int) -> List[ChildExpense]:
    return db.query(ChildExpense).filter(ChildExpense.child_id == child_id).order_by(ChildExpense.date.desc()).all()


# --- Saving Goals CRUD ---

def create_saving_goal(db: Session, goal_in: SavingGoalCreate) -> SavingGoal:
    db_goal = SavingGoal(
        child_id=goal_in.child_id,
        title=goal_in.title,
        target_amount=goal_in.target_amount,
        current_saved=goal_in.current_saved,
        target_date=goal_in.target_date,
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal

def get_saving_goals_by_child_id(db: Session, child_id: int) -> List[SavingGoal]:
    return db.query(SavingGoal).filter(SavingGoal.child_id == child_id).order_by(SavingGoal.target_date.asc()).all()


# --- Aggregations & Analytics ---

def generate_expense_summary(db: Session, child_id: int) -> ExpenseSummaryResponse:
    today = datetime.date.today()
    start_of_month = today.replace(day=1)
    
    # Calculate total allowance in the current month
    allowances = db.query(PocketMoneyAllowance).filter(
        PocketMoneyAllowance.child_id == child_id,
        PocketMoneyAllowance.date >= start_of_month,
        PocketMoneyAllowance.date <= today
    ).all()
    total_allowance = sum(a.amount for a in allowances)

    # Calculate total expenses in the current month
    expenses = db.query(ChildExpense).filter(
        ChildExpense.child_id == child_id,
        ChildExpense.date >= start_of_month,
        ChildExpense.date <= today
    ).all()
    total_spent = sum(e.amount for e in expenses)

    remaining_allowance = total_allowance - total_spent
    saving_percentage = (remaining_allowance / total_allowance * 100.0) if total_allowance > 0 else 0.0

    # Spending by category
    spending_by_category: Dict[str, float] = {}
    for e in expenses:
        cat = e.category
        spending_by_category[cat] = spending_by_category.get(cat, 0.0) + e.amount

    # Daily average & Projected month-end spending
    days_passed = today.day
    avg_daily = round(total_spent / days_passed, 2) if days_passed > 0 else 0.0
    _, total_days_in_month = calendar.monthrange(today.year, today.month)
    projected = round(avg_daily * total_days_in_month, 2)

    return ExpenseSummaryResponse(
        total_allowance=round(total_allowance, 2),
        total_spent=round(total_spent, 2),
        remaining_allowance=round(remaining_allowance, 2),
        spending_by_category=spending_by_category,
        saving_percentage=round(saving_percentage, 1),
        average_daily_spending=avg_daily,
        projected_month_end_spending=projected
    )

def get_financial_education_tips(db: Session, child_id: int) -> Optional[FinancialEducationResponse]:
    child_profile = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    if not child_profile:
        return None

    age_group = classify_age_group(child_profile.age)

    if age_group in ("EARLY_CHILDHOOD", "PRIMARY_SCHOOL"):
        tips = [
            "Saving Box: Put away half of the pocket money you receive in a savings box/jar.",
            "Wants vs. Needs: Needs are things you must have to live (like healthy food). Wants are things that are fun to have (like toys). Try to prioritize needs first!",
            "Goal Tracker: Choose a small toy or game you want, draw it, and track how many coins you save for it each week."
        ]
        split = {"Spend": 50.0, "Save": 50.0}
    elif age_group in ("MIDDLE_SCHOOL", "HIGH_SCHOOL"):
        tips = [
            "Budget Rules: Use the simple 50/30/20 rule: 50% for needs (school books, bus transport), 30% for wants (games, friends, movies), and 20% for your savings goals.",
            "Compare Before Buying: Before buying subscription memberships or games, check if there's a cheaper alternative.",
            "Track Every Rupee: Write down all of your expenses daily. You'll be surprised to see how small purchases add up over the month!"
        ]
        split = {"Needs (School/Transport)": 50.0, "Wants (Entertainment/Gaming)": 30.0, "Savings (Future Goals)": 20.0}
    else:  # COLLEGE
        tips = [
            "Independent Budgeting: Categorize and track all spending. Ensure subscriptions (music, video, gym) are within your monthly wants allocation.",
            "Emergency Buffer: Keep an emergency fund containing at least one month of pocket money for unexpected occurrences.",
            "Saving Goal Planning: Before requesting big amounts from parents, check if you can allocate 25% of your allowance monthly to fund it.",
            "Smart Subscriptions: Periodically review recurring subscriptions. If you haven't used a service in the past 30 days, pause or cancel it."
        ]
        split = {"Essential Living (Food/Bills)": 50.0, "Discretionary (Shopping/Hangouts)": 30.0, "Savings & Investments": 20.0}

    return FinancialEducationResponse(
        age_group=age_group,
        tips=tips,
        recommended_budget_split=split
    )

def get_saving_goals_analysis(db: Session, child_id: int) -> SavingAnalysisResponse:
    goals = get_saving_goals_by_child_id(db, child_id)
    progress_list = []
    
    for g in goals:
        remaining = max(0.0, g.target_amount - g.current_saved)
        pct = round((g.current_saved / g.target_amount * 100.0), 1) if g.target_amount > 0 else 100.0
        
        today = datetime.date.today()
        days_left = (g.target_date - today).days
        days_left = max(0, days_left)
        
        # Calculate daily savings rate needed to reach goal
        daily_saving_needed = round(remaining / days_left, 2) if days_left > 0 else remaining
        
        progress_list.append({
            "id": g.id,
            "title": g.title,
            "target_amount": g.target_amount,
            "current_saved": g.current_saved,
            "target_date": g.target_date,
            "percentage_completed": pct,
            "days_remaining": days_left,
            "daily_saving_needed": daily_saving_needed
        })
        
    return SavingAnalysisResponse(
        total_goals=len(goals),
        goals_progress=progress_list
    )


# --- Cross-Agent API Stubs (Father Agent Integration) ---

def request_parental_funding_interface(db: Session, child_id: int, amount: float, purpose: str) -> Dict[str, Any]:
    """
    Service Interface Stub prepared for live integration with the Father Agent's Finance API.
    In the future, this will initiate a REST call to the Father Agent to check if the family budget allows
    a funding request of the specified amount.
    """
    child_profile = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    family_id = child_profile.family_id if child_profile else "unknown_family"
    
    return {
        "status": "affordability_check_pending",
        "message": f"Funding request of ₹{amount} for '{purpose}' submitted to Father Agent.",
        "family_id": family_id,
        "child_id": child_id,
        "amount": amount,
        "purpose": purpose,
        "live_cross_agent_call_ready": False,
        "requires_affordability_approval": True,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
