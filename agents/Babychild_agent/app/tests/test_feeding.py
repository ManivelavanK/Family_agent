import pytest
from datetime import datetime, date, timedelta

@pytest.fixture
def test_baby_id(client):
    # Setup: Create a baby profile to link feedings to
    payload = {
        "family_id": 1,
        "name": "Feeding Test Baby",
        "date_of_birth": str(date.today() - timedelta(days=30))
    }
    res = client.post("/api/v1/baby/create", json=payload)
    return res.json()["data"]["id"]


def test_create_feeding_success(client, test_baby_id):
    payload = {
        "baby_id": test_baby_id,
        "feeding_type": "formula",
        "food_name": "Similac",
        "quantity_ml": 120.0,
        "duration_minutes": 15,
        "feeding_time": str(datetime.now()),
        "notes": "Fed well"
    }
    response = client.post("/api/v1/feeding/create", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["feeding_type"] == "formula"
    assert data["data"]["quantity_ml"] == 120.0


def test_get_feeding_history(client, test_baby_id):
    # Log a feeding
    payload = {
        "baby_id": test_baby_id,
        "feeding_type": "breast",
        "duration_minutes": 20,
        "feeding_time": str(datetime.now())
    }
    client.post("/api/v1/feeding/create", json=payload)

    # Get history
    response = client.get(f"/api/v1/feeding/{test_baby_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) >= 1
    assert data["data"][0]["feeding_type"] == "breast"


def test_generate_today_summary(client, test_baby_id):
    # Log today's feeding
    payload_today = {
        "baby_id": test_baby_id,
        "feeding_type": "formula",
        "quantity_ml": 150.0,
        "feeding_time": str(datetime.now())
    }
    client.post("/api/v1/feeding/create", json=payload_today)

    # Log yesterday's feeding (should not count in today's sum)
    payload_yesterday = {
        "baby_id": test_baby_id,
        "feeding_type": "solid",
        "quantity_ml": 200.0,
        "feeding_time": str(datetime.now() - timedelta(days=1))
    }
    client.post("/api/v1/feeding/create", json=payload_yesterday)

    # Get today's summary
    response = client.get(f"/api/v1/feeding/today/{test_baby_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["total_feedings"] >= 1
    # Verify yesterday's 200ml solid is excluded from summary
    # Only the 150ml (plus any other run in this test session) should be returned
    assert data["data"]["total_quantity_ml"] >= 150.0
    assert all(
        datetime.fromisoformat(f["feeding_time"]).date() == date.today()
        for f in data["data"]["feedings"]
    )


def test_update_feeding(client, test_baby_id):
    # Log feeding
    payload = {
        "baby_id": test_baby_id,
        "feeding_type": "solid",
        "food_name": "Rice Cereal",
        "quantity_ml": 50.0,
        "feeding_time": str(datetime.now())
    }
    res = client.post("/api/v1/feeding/create", json=payload)
    feeding_id = res.json()["data"]["id"]

    # Update feeding
    update_payload = {
        "food_name": "Oatmeal Cereal",
        "quantity_ml": 80.0
    }
    response = client.put(f"/api/v1/feeding/{feeding_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["food_name"] == "Oatmeal Cereal"
    assert data["data"]["quantity_ml"] == 80.0


def test_delete_feeding(client, test_baby_id):
    # Log feeding
    payload = {
        "baby_id": test_baby_id,
        "feeding_type": "breast",
        "feeding_time": str(datetime.now())
    }
    res = client.post("/api/v1/feeding/create", json=payload)
    feeding_id = res.json()["data"]["id"]

    # Delete feeding
    response = client.delete(f"/api/v1/feeding/{feeding_id}")
    assert response.status_code == 200
    assert response.json()["success"] is True

    # Get history should be empty or exclude deleted
    history = client.get(f"/api/v1/feeding/{test_baby_id}")
    assert all(f["id"] != feeding_id for f in history.json()["data"])


def test_invalid_feeding_type(client, test_baby_id):
    payload = {
        "baby_id": test_baby_id,
        "feeding_type": "juice",  # invalid type
        "feeding_time": str(datetime.now())
    }
    response = client.post("/api/v1/feeding/create", json=payload)
    assert response.status_code == 422
    assert "Feeding type must be one of" in response.text


def test_negative_quantity_validation(client, test_baby_id):
    payload = {
        "baby_id": test_baby_id,
        "feeding_type": "formula",
        "quantity_ml": -10.0,  # invalid
        "feeding_time": str(datetime.now())
    }
    response = client.post("/api/v1/feeding/create", json=payload)
    assert response.status_code == 422
    assert "Quantity cannot be negative" in response.text


def test_baby_not_found_validation(client):
    payload = {
        "baby_id": 99999,  # invalid
        "feeding_type": "formula",
        "feeding_time": str(datetime.now())
    }
    response = client.post("/api/v1/feeding/create", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
