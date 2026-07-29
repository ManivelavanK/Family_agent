import os
import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import Base, get_db
# Import models to ensure tables are created
from app.models.profile import ChildProfile
from app.models.pocket_money import PocketMoneyAllowance, ChildExpense, SavingGoal

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_pocket_money.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(name="session")
def session_fixture():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        if os.path.exists("test_pocket_money.db"):
            try:
                os.remove("test_pocket_money.db")
            except Exception:
                pass

@pytest.fixture(name="client")
def client_fixture(session):
    def override_get_db():
        try:
            yield session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_pocket_money_and_expenses(client):
    # 1. Create Child Profile (Middle School: 14-year-old)
    child_payload = {
        "family_id": "fam_money",
        "name": "Oliver",
        "date_of_birth": "2012-01-01",
        "age": 12,
        "gender": "Male",
        "parent_contact": "999-999-9999"
    }
    res_child = client.post("/children/profile", json=child_payload)
    assert res_child.status_code == 201
    child_id = res_child.json()["id"]

    # 2. Allocate Allowance
    today = date.today()
    allowance_payload = {
        "family_id": "fam_money",
        "child_id": child_id,
        "amount": 2000.0,
        "frequency": "Monthly",
        "date": str(today.replace(day=1))
    }
    res_all = client.post("/children/pocket-money", json=allowance_payload)
    assert res_all.status_code == 201

    # 3. Log Expenses
    expense_1 = {
        "family_id": "fam_money",
        "child_id": child_id,
        "amount": 300.0,
        "category": "Food",
        "description": "Lunch with friends",
        "date": str(today)
    }
    expense_2 = {
        "family_id": "fam_money",
        "child_id": child_id,
        "amount": 200.0,
        "category": "Gaming",
        "description": "Game skins purchase",
        "date": str(today)
    }
    client.post("/children/expenses", json=expense_1)
    client.post("/children/expenses", json=expense_2)

    # 4. Verify Summary Endpoint
    res_summary = client.get(f"/children/expenses/{child_id}/summary")
    assert res_summary.status_code == 200
    summary = res_summary.json()
    assert summary["total_allowance"] == 2000.0
    assert summary["total_spent"] == 500.0
    assert summary["remaining_allowance"] == 1500.0
    assert summary["saving_percentage"] == 75.0
    assert summary["spending_by_category"]["Food"] == 300.0
    assert summary["spending_by_category"]["Gaming"] == 200.0

    # 5. Verify Budgeting Education Advice
    res_budget = client.get(f"/children/expenses/{child_id}/budget")
    assert res_budget.status_code == 200
    budget = res_budget.json()
    assert budget["age_group"] == "MIDDLE_SCHOOL"
    # Ensure 50/30/20 budget recommendation splits exist
    assert any("50/30/20" in tip for tip in budget["tips"])

    # 6. Verify Saving Goal Analysis
    target_date = today + timedelta(days=10)
    goal_payload = {
        "child_id": child_id,
        "title": "Bicycle",
        "target_amount": 5000.0,
        "current_saved": 1000.0,
        "target_date": str(target_date)
    }
    client.post("/children/expenses/saving-goal", json=goal_payload)

    res_goal = client.get(f"/children/expenses/{child_id}/saving-analysis")
    assert res_goal.status_code == 200
    analysis = res_goal.json()
    assert analysis["total_goals"] == 1
    goal_item = analysis["goals_progress"][0]
    assert goal_item["percentage_completed"] == 20.0
    assert goal_item["days_remaining"] == 10
    # Daily saving needed: (5000 - 1000) / 10 = 400.0
    assert goal_item["daily_saving_needed"] == 400.0

    # 7. Verify Parental Funding Integration Interface
    res_funding = client.post(
        f"/children/expenses/{child_id}/request-funding",
        params={"amount": 4000.0, "purpose": "Educational Course"}
    )
    assert res_funding.status_code == 202
    funding_data = res_funding.json()
    assert funding_data["status"] == "affordability_check_pending"
    assert funding_data["amount"] == 4000.0
    assert funding_data["live_cross_agent_call_ready"] is False
