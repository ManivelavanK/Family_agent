import os
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import Base, get_db
# Import models to ensure tables are created
from app.models.profile import ChildProfile
from app.models.study import StudyMaterial, StudySession

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_study.db"
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
        if os.path.exists("test_study.db"):
            try:
                os.remove("test_study.db")
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

def test_study_materials_crud(client):
    # 1. Create Child Profile
    child_payload = {
        "family_id": "fam_study",
        "name": "Emily",
        "date_of_birth": "2012-01-01",
        "age": 14,
        "gender": "Female",
        "parent_contact": "999-999-9999"
    }
    res_child = client.post("/children/profile", json=child_payload)
    assert res_child.status_code == 201
    child_id = res_child.json()["id"]

    # 2. Add Material
    material_payload = {
        "child_id": child_id,
        "subject": "Mathematics",
        "title": "Calculus Notes",
        "material_type": "Notes",
        "file_link_reference": "https://example.com/calculus-notes.pdf",
        "chapter": "Chapter 1",
        "topic": "Limits",
        "difficulty": "Hard",
        "exam": "AP Calculus",
        "status": "UNREAD"
    }
    res_mat = client.post("/children/study/material", json=material_payload)
    assert res_mat.status_code == 201
    material_id = res_mat.json()["id"]

    # 3. List Materials
    res_list = client.get(f"/children/study/materials/{child_id}")
    assert res_list.status_code == 200
    assert len(res_list.json()) == 1
    assert res_list.json()[0]["title"] == "Calculus Notes"

    # 4. Update Material
    update_payload = {"status": "IN_PROGRESS"}
    res_update = client.put(f"/children/study/material/{material_id}", json=update_payload)
    assert res_update.status_code == 200
    assert res_update.json()["status"] == "IN_PROGRESS"

    # 5. Delete Material
    res_del = client.delete(f"/children/study/material/{material_id}")
    assert res_del.status_code == 204

def test_study_sessions_and_reports(client):
    # 1. Create Child Profile
    child_payload = {
        "family_id": "fam_study",
        "name": "Frank",
        "date_of_birth": "2010-01-01",
        "age": 16,
        "gender": "Male",
        "parent_contact": "999-999-9999"
    }
    res_child = client.post("/children/profile", json=child_payload)
    child_id = res_child.json()["id"]

    # 2. Log Study Sessions (Mathematics: 5 hours/300 mins; Physics: 1 hour/60 mins; English: 30 mins)
    now = datetime.now()
    
    # Mathematics session (300 minutes)
    math_session = {
        "child_id": child_id,
        "subject": "Mathematics",
        "topic": "Algebra",
        "start_time": str(now - timedelta(minutes=300)),
        "end_time": str(now),
        "focus_score": 90,
        "notes": "Intense practice"
    }
    
    # Physics session (60 minutes)
    physics_session = {
        "child_id": child_id,
        "subject": "Physics",
        "topic": "Mechanics",
        "start_time": str(now - timedelta(days=1, minutes=60)),
        "end_time": str(now - timedelta(days=1)),
        "focus_score": 80,
        "notes": "Vectors review"
    }
    
    # English session (30 minutes)
    english_session = {
        "child_id": child_id,
        "subject": "English",
        "topic": "Grammar",
        "start_time": str(now - timedelta(days=2, minutes=30)),
        "end_time": str(now - timedelta(days=2)),
        "focus_score": 70,
        "notes": "Verbs exercises"
    }

    client.post("/children/study/session", json=math_session)
    client.post("/children/study/session", json=physics_session)
    client.post("/children/study/session", json=english_session)

    # 3. Get Sessions
    res_sessions = client.get(f"/children/study/sessions/{child_id}")
    assert res_sessions.status_code == 200
    assert len(res_sessions.json()) == 3

    # 4. Get Study Report & Balance Check
    res_report = client.get(f"/children/study/report/{child_id}")
    assert res_report.status_code == 200
    report = res_report.json()

    assert report["weekly_study_time_minutes"] == 390
    assert report["subject_wise_study_time_minutes"]["Mathematics"] == 300
    assert report["subject_wise_study_time_minutes"]["Physics"] == 60
    assert report["subject_wise_study_time_minutes"]["English"] == 30
    assert report["most_studied_subject"] == "Mathematics"
    assert report["least_studied_subject"] == "English"
    
    # Average focus: (90 + 80 + 70) / 3 = 80.0
    assert report["average_focus_score"] == 80.0
    
    # Consistency: 3 unique days out of 7 = (3/7)*100 = 42.9%
    assert report["study_consistency_percentage"] == 42.9

    # Balance Analyzer check: Max is Math (300 mins).
    # Physics is 60 mins which is 20% of Math (< 30%). English is 30 mins which is 10% (< 30%).
    # So both should trigger recommendations.
    recs = report["balance_recommendations"]
    assert len(recs) >= 2
    assert any("Physics" in r for r in recs)
    assert any("English" in r for r in recs)
