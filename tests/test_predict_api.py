"""Prediction route (tasks 3.4, 3.5) + as-of (crosshair-as-of-prediction-4h-plus)."""

import asyncio
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.cache.candles import CandleStore
from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "candles.db"))
    with TestClient(app) as c:
        yield c


async def _seed_4h_candles(db_path: Path, n: int = 45) -> int:
    store = CandleStore(db_path)
    await store.init()
    base = 1_700_000_000_000
    step = 14_400_000  # 4h in ms
    candles = [
        {
            "open_time_ms": base + i * step,
            "open": 100.0 + i * 0.1,
            "high": 101.0 + i * 0.1,
            "low": 99.0 + i * 0.1,
            "close": 100.5 + i * 0.1,
            "volume": 1_000.0 + i,
        }
        for i in range(n)
    ]
    await store.upsert_candles("BTC/USDT", "4h", candles)
    return candles[-1]["open_time_ms"]


def test_predict_unavailable_without_model(client):
    r = client.get("/predict", params={"symbol": "BTC/USDT", "interval": "1m"})
    assert r.status_code == 200
    body = r.json()
    assert body["available"] is False
    assert body.get("reason")
    assert "not financial advice" in body.get("disclaimer", "").lower()
    assert body.get("prediction_anchor") == "latest"


def test_predict_as_of_rejects_short_interval(client):
    r = client.get(
        "/predict",
        params={
            "symbol": "BTC/USDT",
            "interval": "1m",
            "as_of": "2024-01-01T00:00:00+00:00",
        },
    )
    assert r.status_code == 400
    assert r.json()["detail"]["reason"] == "unsupported_interval_for_as_of"


def test_predict_as_of_rejects_invalid_iso(client):
    r = client.get(
        "/predict",
        params={"symbol": "BTC/USDT", "interval": "4h", "as_of": "invalid-date"},
    )
    assert r.status_code == 400
    assert r.json()["detail"]["reason"] == "invalid_as_of"


def test_predict_as_of_rejects_unknown_bar(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "candles.db"))
    asyncio.run(_seed_4h_candles(tmp_path / "candles.db", n=40))
    with TestClient(app) as client:
        r = client.get(
            "/predict",
            params={
                "symbol": "BTC/USDT",
                "interval": "4h",
                "as_of": "1999-01-01T00:00:00+00:00",
            },
        )
    assert r.status_code == 400
    assert r.json()["detail"]["reason"] == "as_of_not_in_series"


def test_predict_as_of_unavailable_no_model_when_valid_bar(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "candles.db"))
    last_open = asyncio.run(_seed_4h_candles(tmp_path / "candles.db", n=45))
    from datetime import datetime, timezone

    as_of_iso = datetime.fromtimestamp(last_open / 1000.0, tz=timezone.utc).isoformat().replace("+00:00", "Z")
    with TestClient(app) as client:
        r = client.get(
            "/predict",
            params={"symbol": "BTC/USDT", "interval": "4h", "as_of": as_of_iso},
        )
    assert r.status_code == 200
    body = r.json()
    assert body["available"] is False
    assert body.get("reason") == "no_model"
    assert body.get("prediction_anchor") == "as_of"
