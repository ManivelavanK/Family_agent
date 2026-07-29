import pytest
from datetime import date, timedelta

@pytest.fixture
def test_baby_id(client):
    # Setup: Create a baby profile to link vaccination records to
    payload = {
        "family_id": 1,
        "name": "Vaccine Test Baby",
        "date_of_birth": str(date.today() - timedelta(days=45))
    }
    res = client.post("/api/v1/baby/create", json=payload)
    return res.json()["data"]["id"]


def test_create_vaccination_record_success(client, test_baby_id):
    payload = {
        "baby_id": test_baby_id,
        "vaccine_name": "MMR",
        "dose_number": 1,
        "due_date": str(date.today() + timedelta(days=10)),
        "status": "pending",
        "hospital": "City Hospital",
        "doctor_name": "Dr. Davis",
        "notes": "First dose MMR"
    }
    response = client.post("/api/v1/vaccine/create", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["vaccine_name"] == "MMR"
    assert data["data"]["status"] == "pending"


def test_get_vaccination_history(client, test_baby_id):
    payload = {
        "baby_id": test_baby_id,
        "vaccine_name": "Polio",
        "dose_number": 2,
        "due_date": str(date.today() - timedelta(days=5)),
        "status": "completed",
        "completed_date": str(date.today() - timedelta(days=5))
    }
    client.post("/api/v1/vaccine/create", json=payload)

    response = client.get(f"/api/v1/vaccine/{test_baby_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) >= 1
    assert data["data"][0]["vaccine_name"] == "Polio"


def test_get_upcoming_vaccinations(client, test_baby_id):
    # Upcoming pending vaccine (due tomorrow)
    payload_upcoming = {
        "baby_id": test_baby_id,
        "vaccine_name": "Hepatitis B",
        "due_date": str(date.today() + timedelta(days=1)),
        "status": "pending"
    }
    client.post("/api/v1/vaccine/create", json=payload_upcoming)

    # Past completed vaccine (should not show up in upcoming)
    payload_past = {
        "baby_id": test_baby_id,
        "vaccine_name": "Rotavirus",
        "due_date": str(date.today() - timedelta(days=10)),
        "status": "completed",
        "completed_date": str(date.today() - timedelta(days=10))
    }
    client.post("/api/v1/vaccine/create", json=payload_past)

    response = client.get(f"/api/v1/vaccine/upcoming/{test_baby_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    # Verify Rotavirus is excluded and Hepatitis B is included
    assert any(v["vaccine_name"] == "Hepatitis B" for v in data["data"])
    assert all(v["vaccine_name"] != "Rotavirus" for v in data["data"])


def test_complete_vaccination(client, test_baby_id):
    # Log record
    payload = {
        "baby_id": test_baby_id,
        "vaccine_name": "BCG",
        "due_date": str(date.today()),
        "status": "pending"
    }
    res = client.post("/api/v1/vaccine/create", json=payload)
    vaccination_id = res.json()["data"]["id"]

    # Mark completed
    response = client.put(f"/api/v1/vaccine/complete/{vaccination_id}?completed_date={date.today()}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "completed"
    assert data["data"]["completed_date"] == str(date.today())


def test_delete_vaccination(client, test_baby_id):
    payload = {
        "baby_id": test_baby_id,
        "vaccine_name": "DTaP",
        "due_date": str(date.today()),
        "status": "pending"
    }
    res = client.post("/api/v1/vaccine/create", json=payload)
    vaccination_id = res.json()["data"]["id"]

    response = client.delete(f"/api/v1/vaccine/{vaccination_id}")
    assert response.status_code == 200
    assert response.json()["success"] is True

    # Try to fetch history
    get_res = client.get(f"/api/v1/vaccine/{test_baby_id}")
    assert all(r["id"] != vaccination_id for r in get_res.json()["data"])


def test_invalid_status_validation(client, test_baby_id):
    payload = {
        "baby_id": test_baby_id,
        "vaccine_name": "Flu",
        "due_date": str(date.today()),
        "status": "unknown"  # invalid status
    }
    response = client.post("/api/v1/vaccine/create", json=payload)
    assert response.status_code == 422
    assert "Status must be one of" in response.text


def test_missing_vaccine_name_validation(client, test_baby_id):
    payload = {
        "baby_id": test_baby_id,
        "vaccine_name": "",  # missing name
        "due_date": str(date.today()),
        "status": "pending"
    }
    response = client.post("/api/v1/vaccine/create", json=payload)
    assert response.status_code == 422
    assert "Vaccine name is required" in response.text


def test_family_ownership_validation(client, test_baby_id):
    response = client.get(f"/api/v1/vaccine/{test_baby_id}?family_id=999")
    assert response.status_code == 403
