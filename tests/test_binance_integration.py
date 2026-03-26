"""Optional smoke test against Binance public REST (task 2.5)."""

import os

import httpx
import pytest


@pytest.mark.asyncio
@pytest.mark.skipif(
    os.environ.get("BINANCE_INTEGRATION", "").lower() not in ("1", "true", "yes"),
    reason="Set BINANCE_INTEGRATION=1 to run live Binance smoke test",
)
async def test_public_klines_smoke():
    async with httpx.AsyncClient(base_url="https://api.binance.com", timeout=30.0) as client:
        r = await client.get("/api/v3/klines", params={"symbol": "BTCUSDT", "interval": "1m", "limit": 3})
    r.raise_for_status()
    body = r.json()
    assert isinstance(body, list) and len(body) >= 1
