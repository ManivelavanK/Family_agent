import os
import json
import logging
import re
from datetime import date
from sqlalchemy.orm import Session
from app.models.profile import ChildProfile
from app.models.pocket_money import SavingGoal, PocketMoneyAllowance
from app.ai.groq_service import _get_groq_client
from app.services.cross_agent_service import create_child_expense, create_education_expense
from app.schemas.cross_agent import ChildExpenseCreate, ChildEducationExpenseCreate

logger = logging.getLogger(__name__)

def handle_query(db: Session, child_id: int, query: str) -> dict:
    child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    child_name = child.name if child else "Child"
    family_id = child.family_id if child else "family_1"

    # Affordability check
    if "afford" in query.lower() or "price" in query.lower() or "cost" in query.lower() or "buy" in query.lower() or "course" in query.lower():
        # Extract amount from query (e.g. 2000)
        amount = 0.0
        match = re.search(r"(?:₹|\$|rs\.?|rupees|)\s*([\d,]+)", query.lower())
        if match:
            amount = float(match.group(1).replace(",", ""))

        # Check total saving/allowance
        allowances = db.query(PocketMoneyAllowance).filter(PocketMoneyAllowance.child_id == child_id).all()
        allowance_total = sum(a.amount for a in allowances)

        goals = db.query(SavingGoal).filter(SavingGoal.child_id == child_id).all()
        total_saved = sum(g.current_saved for g in goals)

        can_afford = (allowance_total + total_saved) >= amount

        # If it's a course/education, log education expense request (intended for Father)
        is_education = "course" in query.lower() or "book" in query.lower() or "study" in query.lower() or "school" in query.lower()
        if is_education and amount > 0:
            edu_expense_data = ChildEducationExpenseCreate(
                family_id=family_id,
                child_id=child_id,
                amount=amount,
                expense_type="Course fees" if "course" in query.lower() else "Books",
                description=f"Affordability inquiry: {query}",
                date=date.today()
            )
            create_education_expense(db=db, education_expense_in=edu_expense_data)

        reply = f"Hi {child_name}, looking at the cost of ₹{amount:.2f}: "
        if can_afford:
            reply += f"Yes, you have enough funds (Total Pocket Money + Savings: ₹{(allowance_total + total_saved):.2f})."
        else:
            reply += f"No, you currently only have ₹{(allowance_total + total_saved):.2f}. "
            if is_education:
                reply += "I have submitted an education affordability request to your Father Agent for review."
            else:
                reply += "Try saving up a bit more to achieve this goal!"

        return {
            "agent": "Finance Agent",
            "reply": reply,
            "actions": {
                "inquired_amount": amount,
                "can_afford": can_afford,
                "is_education": is_education
            }
        }

    # Log expense
    amount = 0.0
    category = "Other"
    description = "Logged via assistant"

    # Use LLM to extract expense details if key is available
    client = _get_groq_client()
    if client:
        try:
            prompt = f"""
            Analyze this child expense statement: "{query}"
            Extract:
            1. amount: float value of expense (e.g. 300)
            2. category: one of [Food, Transport, Education, Entertainment, Shopping, Gaming, Subscriptions, Friends, Emergency, Other]
            3. description: string summary
            
            Return ONLY a raw JSON object:
            {{
              "amount": 300.0,
              "category": "Food",
              "description": "description of spent money"
            }}
            """
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            parsed = json.loads(response.choices[0].message.content.strip())
            amount = float(parsed.get("amount") or 0.0)
            category = parsed.get("category") or "Other"
            description = parsed.get("description") or "Logged via assistant"
        except Exception as e:
            logger.error(f"Groq parsing failed in finance agent: {e}")
            # fallback to regex
            match = re.search(r"(\d+)", query)
            if match:
                amount = float(match.group(1))
    else:
        # Regex fallback
        match = re.search(r"(\d+)", query)
        if match:
            amount = float(match.group(1))

    if amount > 0:
        expense_data = ChildExpenseCreate(
            family_id=family_id,
            child_id=child_id,
            amount=amount,
            category=category,
            description=description,
            date=date.today()
        )
        db_expense = create_child_expense(db=db, expense_in=expense_data)
        reply = f"Got it! I have logged an expense of ₹{db_expense.amount:.2f} under '{db_expense.category}'."
    else:
        reply = "I couldn't understand the amount you spent. Could you specify it clearly? E.g., 'I spent ₹300 today'."

    return {
        "agent": "Finance Agent",
        "reply": reply,
        "actions": {
            "logged_amount": amount,
            "category": category
        }
    }
