import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import Base, get_db
from app.models.profile import ChildProfile

import os

# Use a file-based SQLite database for testing to avoid connection sharing issues in memory
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
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
        if os.path.exists("test.db"):
            try:
                os.remove("test.db")
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

def test_create_and_read_profile(client):
    payload = {
        "family_id": "fam_123",
        "name": "Alice",
        "date_of_birth": "2018-05-15",
        "age": 8,
        "gender": "Female",
        "class_or_year": "Grade 3",
        "school_or_college": "Greenwood Elementary",
        "blood_group": "O+",
        "allergies": "Peanuts",
        "emergency_contact": "999-999-9999",
        "parent_contact": "888-888-8888",
        "interests": ["drawing", "swimming"],
        "career_interest": "Astronaut",
        "daily_wake_time": "07:00:00",
        "daily_sleep_time": "20:30:00"
    }
    
    # 1. Create Profile
    res_create = client.post("/children/profile", json=payload)
    assert res_create.status_code == 201
    data = res_create.json()
    assert data["name"] == "Alice"
    assert data["age"] == 8
    assert data["education_stage"] == "PRIMARY_SCHOOL"  # Auto-classification check
    child_id = data["id"]
    
    # 2. Get Profile by family_id
    res_fam = client.get("/children/profile/fam_123")
    assert res_fam.status_code == 200
    assert len(res_fam.json()) == 1
    assert res_fam.json()[0]["id"] == child_id
    
    # 3. Get Profile by family_id and child_id
    res_child = client.get(f"/children/profile/fam_123/{child_id}")
    assert res_child.status_code == 200
    assert res_child.json()["name"] == "Alice"
    
    # 4. Get Adaptive Plan
    res_plan = client.get(f"/children/profile/{child_id}/adaptive-plan")
    assert res_plan.status_code == 200, res_plan.json()
    plan_data = res_plan.json()
    assert plan_data["age_group"] == "PRIMARY_SCHOOL"
    assert "pocket-money" in plan_data["financial_independence_level"]

def test_update_profile(client):
    payload = {
        "family_id": "fam_123",
        "name": "Bob",
        "date_of_birth": "2012-10-10",
        "age": 13,
        "gender": "Male",
        "parent_contact": "888-888-8888"
    }
    res_create = client.post("/children/profile", json=payload)
    assert res_create.status_code == 201
    child_id = res_create.json()["id"]
    assert res_create.json()["education_stage"] == "MIDDLE_SCHOOL"
    
    # Update age to 18 (shifts classification to COLLEGE)
    update_payload = {
        "age": 18
    }
    res_update = client.put(f"/children/profile/{child_id}", json=update_payload)
    assert res_update.status_code == 200
    assert res_update.json()["age"] == 18
    assert res_update.json()["education_stage"] == "COLLEGE"

def test_delete_profile(client):
    payload = {
        "family_id": "fam_123",
        "name": "Charlie",
        "date_of_birth": "2022-01-01",
        "age": 4,
        "gender": "Male",
        "parent_contact": "888-888-8888"
    }
    res_create = client.post("/children/profile", json=payload)
    child_id = res_create.json()["id"]
    
    # Delete child profile
    res_delete = client.delete(f"/children/profile/{child_id}")
    assert res_delete.status_code == 204
    
    # Verify child profile does not exist
    res_get = client.get(f"/children/profile/fam_123/{child_id}")
    assert res_get.status_code == 404
