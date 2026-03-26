"""App bootstrap: FastAPI serves a health check (task 1.1 TDD)."""

from fastapi.testclient import TestClient


def test_health_returns_ok():
    from app.main import app

    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
