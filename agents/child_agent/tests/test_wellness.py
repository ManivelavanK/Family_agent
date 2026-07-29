import os
import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import Base, get_db
from app.models.profile import ChildProfile
from app.models.wellness import DiaryEntry, RelaxationLog

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_wellness_log.db"
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
        if os.path.exists("test_wellness_log.db"):
            try:
                os.remove("test_wellness_log.db")
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


def test_diary_crud_and_privacy_controls(client):
    # 1. Create child profile
    child_payload = {
        "family_id": "fam_wellness",
        "name": "Maya",
        "date_of_birth": "2015-04-12",
        "age": 11,
        "gender": "Female",
        "parent_contact": "555-444-3333"
    }
    res_child = client.post("/children/profile", json=child_payload)
    assert res_child.status_code == 201
    child_id = res_child.json()["id"]

    # 2. Create private diary entry
    diary_payload = {
        "child_id": child_id,
        "date": str(date.today()),
        "title": "My Secret Thoughts",
        "content": "Today I felt a bit nervous about the math quiz, but I did my best.",
        "mood": "anxious",
        "tags": ["school", "math"],
        "share_with_parent": False
    }
    res_create = client.post("/children/diary", json=diary_payload)
    assert res_create.status_code == 201
    entry = res_create.json()
    entry_id = entry["id"]
    assert entry["title"] == "My Secret Thoughts"
    assert entry["mood"] == "anxious"

    # 3. GET /children/diary/{child_id} as child -> retrieves entry
    res_list_child = client.get(f"/children/diary/{child_id}")
    assert res_list_child.status_code == 200
    assert len(res_list_child.json()) == 1

    # 4. Privacy Check: GET /children/diary/{child_id} as parent -> unshared entries NOT exposed
    res_list_parent = client.get(f"/children/diary/{child_id}", params={"requester_role": "parent"})
    assert res_list_parent.status_code == 200
    assert len(res_list_parent.json()) == 0

    # 5. GET /children/diary/{child_id}/{entry_id} as parent -> 403 Forbidden
    res_get_parent = client.get(f"/children/diary/{child_id}/{entry_id}", params={"requester_role": "parent"})
    assert res_get_parent.status_code == 403

    # 6. GET /children/diary/{child_id}/{entry_id} as child -> 200 OK
    res_get_child = client.get(f"/children/diary/{child_id}/{entry_id}")
    assert res_get_child.status_code == 200
    assert res_get_child.json()["id"] == entry_id

    # 7. PUT /children/diary/{entry_id} -> update title and content
    update_payload = {
        "title": "Updated Reflections",
        "content": "I talked to my teacher and feel much better now!",
        "mood": "calm"
    }
    res_update = client.put(f"/children/diary/{entry_id}", json=update_payload)
    assert res_update.status_code == 200
    assert res_update.json()["title"] == "Updated Reflections"
    assert res_update.json()["mood"] == "calm"

    # 8. DELETE /children/diary/{entry_id} -> delete entry
    res_delete = client.delete(f"/children/diary/{entry_id}")
    assert res_delete.status_code == 204

    # Verify entry is deleted
    res_after_del = client.get(f"/children/diary/{child_id}/{entry_id}")
    assert res_after_del.status_code == 404


def test_relaxation_suggestions_and_mood_trend_detection(client):
    # 1. Create Child Profile
    child_res = client.post("/children/profile", json={
        "family_id": "fam_wellness_2",
        "name": "Leo",
        "date_of_birth": "2017-08-20",
        "age": 9,
        "gender": "Male",
        "parent_contact": "555-888-9999"
    })
    child_id = child_res.json()["id"]

    # 2. Get relaxation suggestions
    res_relax = client.get(f"/children/wellness/{child_id}/relaxation")
    assert res_relax.status_code == 200
    data = res_relax.json()
    assert data["child_id"] == child_id
    assert "suggested_activities" in data
    
    activity_types = {act["type"] for act in data["suggested_activities"]}
    expected_types = {"breathing", "short walk", "music", "stretching", "meditation", "hobby", "journaling", "screen break", "social connection"}
    assert expected_types.issubset(activity_types)
    assert "does NOT provide medical or mental health diagnoses" in data["medical_disclaimer"]

    # 3. Simulate repeated negative mood diary entries
    for i in range(3):
        client.post("/children/diary", json={
            "child_id": child_id,
            "date": str(date.today()),
            "title": f"Hard Day #{i+1}",
            "content": "Feeling very stressed and overwhelmed about everything today.",
            "mood": "stressed"
        })

    # 4. Fetch relaxation suggestions again -> mood trend recommendation triggered
    res_relax_trend = client.get(f"/children/wellness/{child_id}/relaxation")
    assert res_relax_trend.status_code == 200
    trend_data = res_relax_trend.json()
    assert trend_data["mood_trend_summary"] is not None
    assert trend_data["support_recommendation"] is not None
    assert "talk with a trusted parent/guardian, school counselor, or qualified" in trend_data["support_recommendation"]

    # 5. Log a completed relaxation activity
    log_res = client.post("/children/wellness/relaxation/log", json={
        "child_id": child_id,
        "date": str(date.today()),
        "activity_type": "breathing",
        "duration_minutes": 5,
        "mood_before": "stressed",
        "mood_after": "calm",
        "notes": "4-4-4 Box Breathing helped me relax."
    })
    assert log_res.status_code == 201
    assert log_res.json()["mood_after"] == "calm"
