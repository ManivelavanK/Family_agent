def test_create_and_get_plan(client):
    payload = {
        "plan_type": "TRAVEL",
        "title": "Family Trip to Ooty",
        "description": "3-day trip for 6 people",
        "start_date": "2026-08-10",
        "end_date": "2026-08-13",
        "number_of_people": 6,
        "budget": 30000.0,
        "status": "DRAFT",
        "location": "Ooty"
    }
    response = client.post("/api/v1/plans", json=payload)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["success"] is True
    plan_id = res_data["data"]["id"]
    assert res_data["data"]["title"] == "Family Trip to Ooty"

    # Get plan by ID
    get_res = client.get(f"/api/v1/plans/{plan_id}")
    assert get_res.status_code == 200
    assert get_res.json()["data"]["id"] == plan_id

def test_update_plan(client):
    payload = {
        "plan_type": "EVENT",
        "title": "Birthday Party",
        "number_of_people": 15,
        "budget": 5000.0
    }
    create_res = client.post("/api/v1/plans", json=payload)
    plan_id = create_res.json()["data"]["id"]

    update_payload = {
        "title": "Grand Birthday Party",
        "budget": 7500.0,
        "status": "PLANNING"
    }
    update_res = client.put(f"/api/v1/plans/{plan_id}", json=update_payload)
    assert update_res.status_code == 200
    assert update_res.json()["data"]["title"] == "Grand Birthday Party"
    assert update_res.json()["data"]["budget"] == 7500.0
    assert update_res.json()["data"]["status"] == "PLANNING"

def test_delete_plan(client):
    payload = {
        "plan_type": "FUNCTION",
        "title": "Anniversary Dinner",
        "number_of_people": 2,
        "budget": 2000.0
    }
    create_res = client.post("/api/v1/plans", json=payload)
    plan_id = create_res.json()["data"]["id"]

    del_res = client.delete(f"/api/v1/plans/{plan_id}")
    assert del_res.status_code == 200

    get_res = client.get(f"/api/v1/plans/{plan_id}")
    assert get_res.status_code == 404

def test_invalid_plan_type(client):
    payload = {
        "plan_type": "CONCERT",  # Invalid enum value
        "title": "Music Night"
    }
    response = client.post("/api/v1/plans", json=payload)
    assert response.status_code == 422
    assert response.json()["success"] is False

def test_invalid_dates(client):
    payload = {
        "plan_type": "TRAVEL",
        "title": "Time Travel Trip",
        "start_date": "2026-08-15",
        "end_date": "2026-08-10"  # end_date before start_date
    }
    response = client.post("/api/v1/plans", json=payload)
    assert response.status_code == 422
    assert response.json()["success"] is False
