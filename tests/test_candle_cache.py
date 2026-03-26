"""SQLite candle cache (task 2.3)."""

import tempfile
from pathlib import Path

import pytest

from app.cache.candles import CandleStore


@pytest.mark.asyncio
async def test_upsert_and_list_returns_chronological():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "c.db"
        store = CandleStore(path)
        await store.init()
        await store.upsert_candles(
            "BTC/USDT",
            "1m",
            [
                {
                    "open_time_ms": 100,
                    "open": 1.0,
                    "high": 1.1,
                    "low": 0.9,
                    "close": 1.05,
                    "volume": 10.0,
                },
                {
                    "open_time_ms": 200,
                    "open": 1.05,
                    "high": 1.2,
                    "low": 1.0,
                    "close": 1.1,
                    "volume": 5.0,
                },
            ],
        )
        rows = await store.list_candles("BTC/USDT", "1m", limit=10)
        assert [r["open_time_ms"] for r in rows] == [100, 200]
        assert rows[-1]["close"] == 1.1
