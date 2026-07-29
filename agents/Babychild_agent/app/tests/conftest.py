import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.database import get_db

@pytest.fixture(scope="session")
def client():
    # Return a TestClient instance using the FastAPI app instance
    with TestClient(app) as c:
        yield c
