def test_itinerary_lifecycle(client):
    plan_res = client.post("/api/v1/plans", json={"plan_type": "TRAVEL", "title": "Ooty Exploration"})
    plan_id = plan_res.json()["data"]["id"]

    item_payload = {
        "date": "2026-08-11",
        "start_time": "09:00:00",
        "end_time": "12:00:00",
        "activity": "Visit Botanical Gardens",
        "location": "Ooty Botanical Garden",
        "estimated_cost": 500.0,
        "notes": "Carry cameras and wear walking shoes"
    }
    itin_res = client.post(f"/api/v1/plans/{plan_id}/itinerary", json=item_payload)
    assert itin_res.status_code == 201
    item_id = itin_res.json()["data"]["id"]
    assert itin_res.json()["data"]["activity"] == "Visit Botanical Gardens"

    get_res = client.get(f"/api/v1/plans/{plan_id}/itinerary")
    assert get_res.status_code == 200
    assert len(get_res.json()["data"]) == 1

    del_res = client.delete(f"/api/v1/itinerary/{item_id}")
    assert del_res.status_code == 200
