def test_participants_lifecycle(client):
    plan_res = client.post("/api/v1/plans", json={"plan_type": "EVENT", "title": "Family Gathering"})
    plan_id = plan_res.json()["data"]["id"]

    p_payload = {
        "name": "Grandma Mary",
        "age": 75,
        "relationship": "Grandmother",
        "special_requirements": "Wheelchair access needed"
    }
    p_res = client.post(f"/api/v1/plans/{plan_id}/participants", json=p_payload)
    assert p_res.status_code == 201
    p_id = p_res.json()["data"]["id"]
    assert p_res.json()["data"]["name"] == "Grandma Mary"

    get_res = client.get(f"/api/v1/plans/{plan_id}/participants")
    assert get_res.status_code == 200
    assert len(get_res.json()["data"]) == 1

    del_res = client.delete(f"/api/v1/participants/{p_id}")
    assert del_res.status_code == 200
