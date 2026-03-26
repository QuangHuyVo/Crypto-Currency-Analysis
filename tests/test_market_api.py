"""HTTP routes for market history (tasks 2.4, 2.5)."""

import httpx
import pytest
from fastapi.testclient import TestClient

from app.binance import klines as klines_mod
from app.binance.klines import parse_klines_json
from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "candles.db"))
    payload = [
        [
            1_700_000_000_000,
            "10",
            "11",
            "9",
            "10.5",
            "1",
            1_700_000_059_999,
            "0",
            0,
            "0",
            "0",
            "0",
        ]
    ]

    async def fake_fetch(client, symbol, interval, limit=500):
        assert symbol == "BTC/USDT"
        assert interval == "1m"
        return parse_klines_json(payload)

    monkeypatch.setattr(klines_mod, "fetch_klines", fake_fetch)

    with TestClient(app) as c:
        yield c


def test_market_history_returns_candles_json(client):
    r = client.get("/market/history", params={"symbol": "BTC/USDT", "interval": "1m", "limit": 1})
    assert r.status_code == 200
    data = r.json()
    assert "candles" in data
    assert len(data["candles"]) == 1
    assert data["candles"][0]["close"] == 10.5
