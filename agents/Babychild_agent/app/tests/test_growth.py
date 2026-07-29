import pytest
from datetime import date, timedelta

@pytest.fixture
def test_baby_id(client):
    # Setup: Create a baby profile to link growth records to
    payload = {
        "family_id": 1,
        "name": "Growth Test Baby",
        "date_of_birth": str(date.today() - timedelta(days=60))
    }
    res = client.post("/api/v1/baby/create", json=payload)
    return res.json()["data"]["id"]


def test_create_growth_record_success(client, test_baby_id):
    payload = {
        "baby_id": test_baby_id,
        "weight_kg": 4.2,
        "height_cm": 54.0,
        "head_circumference_cm": 38.0,
        "record_date": str(date.today())
    }
    response = client.post("/api/v1/growth/create", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["weight_kg"] == 4.2
    assert data["data"]["height_cm"] == 54.0


def test_get_growth_history(client, test_baby_id):
    payload = {
        "baby_id": test_baby_id,
        "weight_kg": 4.5,
        "height_cm": 55.0,
        "record_date": str(date.today() - timedelta(days=1))
    }
    client.post("/api/v1/growth/create", json=payload)

    response = client.get(f"/api/v1/growth/{test_baby_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) >= 1


def test_generate_growth_summary(client, test_baby_id):
    # Clear records if necessary, but in pytest this runs in a session. Let's record.
    # Record 1 (Oldest)
    payload1 = {
        "baby_id": test_baby_id,
        "weight_kg": 3.5,
        "height_cm": 50.0,
        "record_date": str(date.today() - timedelta(days=30))
    }
    client.post("/api/v1/growth/create", json=payload1)

    # Record 2 (Latest)
    payload2 = {
        "baby_id": test_baby_id,
        "weight_kg": 4.5,
        "height_cm": 54.0,
        "record_date": str(date.today())
    }
    client.post("/api/v1/growth/create", json=payload2)

    response = client.get(f"/api/v1/growth/summary/{test_baby_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["total_records"] >= 2
    assert data["data"]["weight_change_kg"] == 1.0
    assert data["data"]["height_change_cm"] == 4.0


def test_update_growth_record(client, test_baby_id):
    payload = {
        "baby_id": test_baby_id,
        "weight_kg": 4.0,
        "height_cm": 53.0,
        "record_date": str(date.today())
    }
    res = client.post("/api/v1/growth/create", json=payload)
    growth_id = res.json()["data"]["id"]

    update_payload = {
        "weight_kg": 4.3,
        "height_cm": 54.5
    }
    response = client.put(f"/api/v1/growth/{growth_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["weight_kg"] == 4.3
    assert data["data"]["height_cm"] == 54.5


def test_delete_growth_record(client, test_baby_id):
    payload = {
        "baby_id": test_baby_id,
        "weight_kg": 4.0,
        "height_cm": 53.0,
        "record_date": str(date.today())
    }
    res = client.post("/api/v1/growth/create", json=payload)
    growth_id = res.json()["data"]["id"]

    response = client.delete(f"/api/v1/growth/{growth_id}")
    assert response.status_code == 200
    assert response.json()["success"] is True

    # Try to fetch deleted
    get_res = client.get(f"/api/v1/growth/{test_baby_id}")
    assert all(r["id"] != growth_id for r in get_res.json()["data"])


def test_negative_weight_validation(client, test_baby_id):
    payload = {
        "baby_id": test_baby_id,
        "weight_kg": -1.0,
        "height_cm": 50.0,
        "record_date": str(date.today())
    }
    response = client.post("/api/v1/growth/create", json=payload)
    assert response.status_code == 422
    assert "Weight cannot be negative" in response.text


def test_negative_height_validation(client, test_baby_id):
    payload = {
        "baby_id": test_baby_id,
        "weight_kg": 4.0,
        "height_cm": -5.0,
        "record_date": str(date.today())
    }
    response = client.post("/api/v1/growth/create", json=payload)
    assert response.status_code == 422
    assert "Height cannot be negative" in response.text


def test_future_date_validation(client, test_baby_id):
    payload = {
        "baby_id": test_baby_id,
        "weight_kg": 4.0,
        "height_cm": 50.0,
        "record_date": str(date.today() + timedelta(days=2))
    }
    response = client.post("/api/v1/growth/create", json=payload)
    assert response.status_code == 422
    assert "Record date cannot be a future date" in response.text


def test_baby_ownership_validation(client, test_baby_id):
    response = client.get(f"/api/v1/growth/{test_baby_id}?family_id=999")
    assert response.status_code == 403


def test_ml_prediction_endpoint(client, test_baby_id):
    # Insufficient data check (less than 2 records)
    res_err = client.post(f"/api/v1/growth/predict/{test_baby_id}")
    assert res_err.status_code == 400
    assert "Insufficient" in res_err.json()["detail"]

    # Add 2 chronological records showing weight gain
    payload1 = {
        "baby_id": test_baby_id,
        "weight_kg": 3.0,
        "height_cm": 50.0,
        "record_date": str(date.today() - timedelta(days=20))
    }
    client.post("/api/v1/growth/create", json=payload1)

    payload2 = {
        "baby_id": test_baby_id,
        "weight_kg": 4.0,
        "height_cm": 53.0,
        "record_date": str(date.today())
    }
    client.post("/api/v1/growth/create", json=payload2)

    # Valid ML prediction check
    response = client.post(f"/api/v1/growth/predict/{test_baby_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["current_weight"] == 4.0
    assert data["data"]["predicted_weight"] > 4.0
    assert data["data"]["growth_trend"] == "upward"
