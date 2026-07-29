import pytest
from datetime import date, timedelta

@pytest.fixture
def test_baby_id(client):
    # Setup: Create a baby profile to link health records to
    payload = {
        "family_id": 1,
        "name": "Health Test Baby",
        "date_of_birth": str(date.today() - timedelta(days=20))
    }
    res = client.post("/api/v1/baby/create", json=payload)
    return res.json()["data"]["id"]


def test_create_health_record_success(client, test_baby_id):
    payload = {
        "baby_id": test_baby_id,
        "temperature_c": 37.2,
        "heart_rate": 110,
        "symptoms": "Mild cough",
        "medicine": "Paracetamol",
        "doctor_name": "Dr. Smith",
        "notes": "Follow-up in 3 days",
        "visit_date": str(date.today())
    }
    response = client.post("/api/v1/health/create", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["temperature_c"] == 37.2
    assert data["data"]["doctor_name"] == "Dr. Smith"


def test_get_health_history(client, test_baby_id):
    payload = {
        "baby_id": test_baby_id,
        "temperature_c": 36.8,
        "visit_date": str(date.today() - timedelta(days=1))
    }
    client.post("/api/v1/health/create", json=payload)

    response = client.get(f"/api/v1/health/{test_baby_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) >= 1


def test_update_health_record(client, test_baby_id):
    payload = {
        "baby_id": test_baby_id,
        "temperature_c": 38.0,
        "visit_date": str(date.today())
    }
    res = client.post("/api/v1/health/create", json=payload)
    health_id = res.json()["data"]["id"]

    update_payload = {
        "temperature_c": 37.5,
        "symptoms": "Fever resolved"
    }
    response = client.put(f"/api/v1/health/{health_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["temperature_c"] == 37.5
    assert data["data"]["symptoms"] == "Fever resolved"


def test_delete_health_record(client, test_baby_id):
    payload = {
        "baby_id": test_baby_id,
        "temperature_c": 36.5,
        "visit_date": str(date.today())
    }
    res = client.post("/api/v1/health/create", json=payload)
    health_id = res.json()["data"]["id"]

    response = client.delete(f"/api/v1/health/{health_id}")
    assert response.status_code == 200
    assert response.json()["success"] is True

    # Check database exclusion
    get_res = client.get(f"/api/v1/health/{test_baby_id}")
    assert all(r["id"] != health_id for r in get_res.json()["data"])


def test_invalid_temperature_validation(client, test_baby_id):
    payload = {
        "baby_id": test_baby_id,
        "temperature_c": -5.0,  # invalid
        "visit_date": str(date.today())
    }
    response = client.post("/api/v1/health/create", json=payload)
    assert response.status_code == 422
    assert "Temperature cannot be negative" in response.text


def test_future_visit_date_validation(client, test_baby_id):
    payload = {
        "baby_id": test_baby_id,
        "temperature_c": 37.0,
        "visit_date": str(date.today() + timedelta(days=2))  # future
    }
    response = client.post("/api/v1/health/create", json=payload)
    assert response.status_code == 422
    assert "Visit date cannot be a future date" in response.text


def test_baby_ownership_validation(client, test_baby_id):
    response = client.get(f"/api/v1/health/{test_baby_id}?family_id=999")
    assert response.status_code == 403


def test_health_summary_aggregation(client, test_baby_id):
    # Record 1 (Older, high temp)
    payload1 = {
        "baby_id": test_baby_id,
        "temperature_c": 39.1,
        "visit_date": str(date.today() - timedelta(days=3)),
        "symptoms": "High fever"
    }
    client.post("/api/v1/health/create", json=payload1)

    # Record 2 (Latest, normal temp)
    payload2 = {
        "baby_id": test_baby_id,
        "temperature_c": 36.6,
        "visit_date": str(date.today()),
        "medicine": "Ibuprofen"
    }
    client.post("/api/v1/health/create", json=payload2)

    response = client.get(f"/api/v1/health/summary/{test_baby_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["total_records"] >= 2
    assert data["data"]["latest_temperature_c"] == 36.6
    assert data["data"]["latest_medicine"] == "Ibuprofen"
