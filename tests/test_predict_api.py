"""Prediction route (tasks 3.4, 3.5)."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "candles.db"))
    with TestClient(app) as c:
        yield c


def test_predict_unavailable_without_model(client):
    r = client.get("/predict", params={"symbol": "BTC/USDT", "interval": "1m"})
    assert r.status_code == 200
    body = r.json()
    assert body["available"] is False
    assert body.get("reason")
    assert "not financial advice" in body.get("disclaimer", "").lower()
