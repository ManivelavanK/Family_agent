import pytest
from datetime import datetime, date, timedelta

@pytest.fixture
def test_baby_id(client):
    # Setup: Create a baby profile to link sleep records to
    payload = {
        "family_id": 1,
        "name": "Sleep Test Baby",
        "date_of_birth": str(date.today() - timedelta(days=15))
    }
    res = client.post("/api/v1/baby/create", json=payload)
    return res.json()["data"]["id"]


def test_create_sleep_record_success(client, test_baby_id):
    now = datetime.now()
    payload = {
        "baby_id": test_baby_id,
        "sleep_type": "day_nap",
        "start_time": str(now - timedelta(hours=1)),
        "end_time": str(now),
        "quality": "good",
        "notes": "Slept calmly"
    }
    response = client.post("/api/v1/sleep/create", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["sleep_type"] == "day_nap"
    assert data["data"]["duration_minutes"] == 60


def test_get_sleep_history(client, test_baby_id):
    now = datetime.now()
    payload = {
        "baby_id": test_baby_id,
        "sleep_type": "night_sleep",
        "start_time": str(now - timedelta(hours=8)),
        "end_time": str(now),
        "quality": "average"
    }
    client.post("/api/v1/sleep/create", json=payload)

    # Get history
    response = client.get(f"/api/v1/sleep/{test_baby_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) >= 1
    assert data["data"][0]["sleep_type"] == "night_sleep"


def test_sleep_duration_auto_calculation(client, test_baby_id):
    now = datetime.now()
    payload = {
        "baby_id": test_baby_id,
        "sleep_type": "day_nap",
        "start_time": str(now - timedelta(minutes=45)),
        "end_time": str(now)
    }
    response = client.post("/api/v1/sleep/create", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["data"]["duration_minutes"] == 45


def test_generate_sleep_summary(client, test_baby_id):
    now = datetime.now()
    # Ensure database has at least one record
    payload = {
        "baby_id": test_baby_id,
        "sleep_type": "night_sleep",
        "start_time": str(now - timedelta(hours=6)),
        "end_time": str(now),
        "quality": "poor"
    }
    client.post("/api/v1/sleep/create", json=payload)

    # Get summary
    response = client.get(f"/api/v1/sleep/summary/{test_baby_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["total_sleep_records"] >= 1
    assert data["data"]["sleep_type_distribution"]["night_sleep"] >= 1
    assert data["data"]["quality_distribution"]["poor"] >= 1


def test_update_sleep(client, test_baby_id):
    now = datetime.now()
    # Log record
    payload = {
        "baby_id": test_baby_id,
        "sleep_type": "day_nap",
        "start_time": str(now - timedelta(hours=1)),
        "end_time": str(now)
    }
    res = client.post("/api/v1/sleep/create", json=payload)
    sleep_id = res.json()["data"]["id"]

    # Update record times
    update_payload = {
        "start_time": str(now - timedelta(hours=2)),
        "end_time": str(now),
        "quality": "good"
    }
    response = client.put(f"/api/v1/sleep/{sleep_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["duration_minutes"] == 120
    assert data["data"]["quality"] == "good"


def test_delete_sleep(client, test_baby_id):
    now = datetime.now()
    # Log record
    payload = {
        "baby_id": test_baby_id,
        "sleep_type": "day_nap",
        "start_time": str(now - timedelta(hours=1)),
        "end_time": str(now)
    }
    res = client.post("/api/v1/sleep/create", json=payload)
    sleep_id = res.json()["data"]["id"]

    # Delete record
    response = client.delete(f"/api/v1/sleep/{sleep_id}")
    assert response.status_code == 200
    assert response.json()["success"] is True

    # Try to delete again
    second_del = client.delete(f"/api/v1/sleep/{sleep_id}")
    assert second_del.status_code == 404


def test_invalid_sleep_type(client, test_baby_id):
    now = datetime.now()
    payload = {
        "baby_id": test_baby_id,
        "sleep_type": "deep_sleep",  # invalid
        "start_time": str(now - timedelta(hours=1)),
        "end_time": str(now)
    }
    response = client.post("/api/v1/sleep/create", json=payload)
    assert response.status_code == 422
    assert "Sleep type must be one of" in response.text


def test_invalid_quality(client, test_baby_id):
    now = datetime.now()
    payload = {
        "baby_id": test_baby_id,
        "sleep_type": "day_nap",
        "start_time": str(now - timedelta(hours=1)),
        "end_time": str(now),
        "quality": "excellent"  # invalid
    }
    response = client.post("/api/v1/sleep/create", json=payload)
    assert response.status_code == 422
    assert "Quality must be one of" in response.text


def test_invalid_time_range(client, test_baby_id):
    now = datetime.now()
    payload = {
        "baby_id": test_baby_id,
        "sleep_type": "day_nap",
        "start_time": str(now),
        "end_time": str(now - timedelta(hours=1))  # end before start
    }
    response = client.post("/api/v1/sleep/create", json=payload)
    assert response.status_code == 422
    assert "End time cannot be before start time" in response.text


def test_baby_ownership_validation(client, test_baby_id):
    # Retrieve history using a family ID that does not own the baby
    response = client.get(f"/api/v1/sleep/{test_baby_id}?family_id=999")
    assert response.status_code == 403
    assert "Forbidden" in response.text or "not belong to this family" in response.text
