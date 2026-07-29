def test_task_lifecycle(client):
    # Create plan first
    plan_res = client.post("/api/v1/plans", json={"plan_type": "TRAVEL", "title": "Trip to Beach"})
    plan_id = plan_res.json()["data"]["id"]

    # Create Task
    task_payload = {
        "title": "Book resort hotel",
        "description": "2 rooms facing ocean",
        "due_date": "2026-08-01",
        "priority": "HIGH",
        "status": "PENDING",
        "estimated_cost": 12000.0
    }
    task_res = client.post(f"/api/v1/plans/{plan_id}/tasks", json=task_payload)
    assert task_res.status_code == 201
    task_data = task_res.json()["data"]
    task_id = task_data["id"]
    assert task_data["title"] == "Book resort hotel"

    # Get Tasks for plan
    get_res = client.get(f"/api/v1/plans/{plan_id}/tasks")
    assert get_res.status_code == 200
    assert len(get_res.json()["data"]) == 1

    # Update Task
    up_res = client.put(f"/api/v1/tasks/{task_id}", json={"status": "COMPLETED"})
    assert up_res.status_code == 200
    assert up_res.json()["data"]["status"] == "COMPLETED"

    # Delete Task
    del_res = client.delete(f"/api/v1/tasks/{task_id}")
    assert del_res.status_code == 200
