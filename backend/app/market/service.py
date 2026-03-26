from __future__ import annotations

import httpx

from app.binance import klines as binance_klines
from app.binance.klines import Candle
from app.binance.throttle import AsyncMinIntervalGate
from app.cache.candles import CandleStore


async def load_klines_for_dashboard(
    store: CandleStore,
    http: httpx.AsyncClient,
    gate: AsyncMinIntervalGate,
    *,
    symbol: str,
    interval: str,
    limit: int,
) -> list[Candle]:
    await gate.acquire()
    remote = await binance_klines.fetch_klines(http, symbol, interval, limit=limit)
    await store.upsert_candles(symbol, interval, remote)
    return await store.list_candles(symbol, interval, limit=limit)
