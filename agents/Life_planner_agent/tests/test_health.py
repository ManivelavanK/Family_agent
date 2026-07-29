def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "KinNest Life Planner Agent is running"
    assert data["data"]["status"] == "healthy"
