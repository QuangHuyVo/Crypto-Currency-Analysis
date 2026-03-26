"""GET /market/symbols."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.market import routes as market_routes


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "candles.db"))

    async def fake_fetch(http):
        return ["AA/USDT", "BTC/USDT", "ETH/USDT", "ZZ/USDT"]

    async def fake_ticker(http):
        return [
            {"symbol": "AAUSDT", "quoteVolume": "1"},
            {"symbol": "BTCUSDT", "quoteVolume": "1000"},
            {"symbol": "ETHUSDT", "quoteVolume": "500"},
            {"symbol": "ZZUSDT", "quoteVolume": "2"},
        ]

    monkeypatch.setattr(market_routes, "fetch_usdt_spot_symbols", fake_fetch)
    monkeypatch.setattr(market_routes, "fetch_ticker_24hr_all", fake_ticker)

    with TestClient(app) as c:
        yield c


def test_market_symbols_returns_sorted_list(client):
    r = client.get("/market/symbols")
    assert r.status_code == 200
    body = r.json()
    assert body["symbols"] == ["AA/USDT", "BTC/USDT", "ETH/USDT", "ZZ/USDT"]
    assert body["top_by_volume"] == ["BTC/USDT", "ETH/USDT", "ZZ/USDT", "AA/USDT"]


def test_market_symbols_filters_by_query(client):
    r = client.get("/market/symbols", params={"q": "eth"})
    assert r.status_code == 200
    assert r.json()["symbols"] == ["ETH/USDT"]


def test_market_symbols_refresh_bypasses_cache(client, monkeypatch):
    calls = {"n": 0}

    async def counting_fetch(http):
        calls["n"] += 1
        return [f"COIN{calls['n']}/USDT"]

    async def dynamic_ticker(http):
        return [{"symbol": f"COIN{calls['n']}USDT", "quoteVolume": "1000"}]

    monkeypatch.setattr(market_routes, "fetch_usdt_spot_symbols", counting_fetch)
    monkeypatch.setattr(market_routes, "fetch_ticker_24hr_all", dynamic_ticker)
    c1 = client.get("/market/symbols")
    assert c1.json()["symbols"] == ["COIN1/USDT"]
    assert c1.json()["top_by_volume"] == ["COIN1/USDT"]
    c2 = client.get("/market/symbols", params={"refresh": "true"})
    assert c2.json()["symbols"] == ["COIN2/USDT"]
    assert c2.json()["top_by_volume"] == ["COIN2/USDT"]
