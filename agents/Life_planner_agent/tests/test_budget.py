def test_budget_item_lifecycle_and_validation(client):
    plan_res = client.post("/api/v1/plans", json={"plan_type": "FUNCTION", "title": "Wedding Ceremony"})
    plan_id = plan_res.json()["data"]["id"]

    # Budget Item Creation
    budget_payload = {
        "category": "Venue & Catering",
        "description": "Hall rental and buffet",
        "estimated_amount": 50000.0,
        "actual_amount": 48000.0,
        "status": "PAID"
    }
    b_res = client.post(f"/api/v1/plans/{plan_id}/budget", json=budget_payload)
    assert b_res.status_code == 201
    item_id = b_res.json()["data"]["id"]

    # Negative budget amount validation check
    invalid_budget = {
        "category": "Decorations",
        "estimated_amount": -500.0  # Invalid negative amount
    }
    inv_res = client.post(f"/api/v1/plans/{plan_id}/budget", json=invalid_budget)
    assert inv_res.status_code == 422

    # Get budget list
    get_res = client.get(f"/api/v1/plans/{plan_id}/budget")
    assert get_res.status_code == 200
    assert len(get_res.json()["data"]) == 1

    # Delete budget item
    del_res = client.delete(f"/api/v1/budget/{item_id}")
    assert del_res.status_code == 200
