"""Binance REST klines: parsing and fetch (tasks 2.1, 2.5)."""

import httpx
import pytest

from app.binance.klines import BinanceClientError, fetch_klines, parse_klines_json, to_binance_symbol


def test_to_binance_symbol_accepts_slash_pair():
    assert to_binance_symbol("BTC/USDT") == "BTCUSDT"


def test_to_binance_symbol_passes_through_compact():
    assert to_binance_symbol("ETHUSDT") == "ETHUSDT"


def test_parse_klines_json_normalizes_utc_ms_and_floats():
    raw = [
        [
            1_700_000_000_000,
            "1.0",
            "2.0",
            "0.5",
            "1.5",
            "100.5",
            1_700_000_059_999,
            "99",
            10,
            "50",
            "25",
            "0",
        ]
    ]
    candles = parse_klines_json(raw)
    assert len(candles) == 1
    c = candles[0]
    assert c["open_time_ms"] == 1_700_000_000_000
    assert c["open"] == 1.0
    assert c["high"] == 2.0
    assert c["low"] == 0.5
    assert c["close"] == 1.5
    assert c["volume"] == 100.5


@pytest.mark.asyncio
async def test_fetch_klines_success_via_mock_transport():
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

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/api/v3/klines")
        assert "BTCUSDT" in str(request.url)
        return httpx.Response(200, json=payload)

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, base_url="https://api.binance.com") as client:
        candles = await fetch_klines(client, "BTC/USDT", "1m", limit=1)
    assert len(candles) == 1
    assert candles[0]["close"] == 10.5


@pytest.mark.asyncio
async def test_fetch_klines_binance_error_raises_structured():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"code": -1121, "msg": "Invalid symbol."})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, base_url="https://api.binance.com") as client:
        with pytest.raises(BinanceClientError) as ei:
            await fetch_klines(client, "BAD", "1m", limit=1)
    assert ei.value.status_code == 400
    assert "Invalid symbol" in ei.value.message
