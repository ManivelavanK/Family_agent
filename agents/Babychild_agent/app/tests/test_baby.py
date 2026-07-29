import pytest
from datetime import date, timedelta

def test_create_baby_success(client):
    payload = {
        "family_id": 1,
        "name": "Jane Doe",
        "date_of_birth": str(date.today() - timedelta(days=60)),
        "gender": "Female",
        "birth_weight": 3.4,
        "blood_group": "O+",
        "allergies": "None",
        "parent_contact": "+1234567890"
    }
    response = client.post("/api/v1/baby/create", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "Jane Doe"
    assert data["data"]["family_id"] == 1
    assert "id" in data["data"]


def test_get_baby_details(client):
    # First create one
    payload = {
        "family_id": 1,
        "name": "Jimmy Doe",
        "date_of_birth": str(date.today() - timedelta(days=10)),
        "gender": "Male",
        "birth_weight": 3.1
    }
    create_res = client.post("/api/v1/baby/create", json=payload)
    baby_id = create_res.json()["data"]["id"]

    # Retrieve
    response = client.get(f"/api/v1/baby/{baby_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "Jimmy Doe"


def test_update_baby(client):
    # First create
    payload = {
        "family_id": 1,
        "name": "Update Test",
        "date_of_birth": str(date.today() - timedelta(days=5)),
        "birth_weight": 2.9
    }
    create_res = client.post("/api/v1/baby/create", json=payload)
    baby_id = create_res.json()["data"]["id"]

    # Update
    update_payload = {
        "name": "Updated Name",
        "birth_weight": 3.5
    }
    response = client.put(f"/api/v1/baby/{baby_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "Updated Name"
    assert data["data"]["birth_weight"] == 3.5


def test_delete_baby(client):
    # Create
    payload = {
        "family_id": 1,
        "name": "To Delete",
        "date_of_birth": str(date.today() - timedelta(days=5))
    }
    create_res = client.post("/api/v1/baby/create", json=payload)
    baby_id = create_res.json()["data"]["id"]

    # Delete
    response = client.delete(f"/api/v1/baby/{baby_id}")
    assert response.status_code == 200
    assert response.json()["success"] is True

    # Try to fetch deleted
    get_res = client.get(f"/api/v1/baby/{baby_id}")
    assert get_res.status_code == 404


def test_invalid_birth_weight(client):
    payload = {
        "family_id": 1,
        "name": "Negative Weight",
        "date_of_birth": str(date.today() - timedelta(days=2)),
        "birth_weight": -1.5
    }
    response = client.post("/api/v1/baby/create", json=payload)
    assert response.status_code == 422
    assert "Input should be greater than or equal to 0" in response.text or "Birth weight cannot be negative" in response.text


def test_future_date_of_birth(client):
    payload = {
        "family_id": 1,
        "name": "Future Born",
        "date_of_birth": str(date.today() + timedelta(days=2))
    }
    response = client.post("/api/v1/baby/create", json=payload)
    assert response.status_code == 422
    assert "Date of birth cannot be a future date" in response.text
