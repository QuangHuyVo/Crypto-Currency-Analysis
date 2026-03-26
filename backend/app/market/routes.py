from __future__ import annotations

import asyncio
import json
import time
from collections.abc import AsyncIterator
from typing import Any, TypedDict

from fastapi import APIRouter, Request
from starlette.responses import StreamingResponse

from app.binance.exchange_info import fetch_usdt_spot_symbols
from app.binance.klines import BinanceClientError
from app.binance.ticker_24hr import fetch_ticker_24hr_all, top_usdt_pairs_by_quote_volume
from app.deps import GateDep, SettingsDep, StoreDep
from app.market.service import load_klines_for_dashboard

SYMBOL_CACHE_TTL_S = 3600.0


class _SymbolCache(TypedDict):
    expires_monotonic: float
    symbols: list[str]
    top_by_volume: list[str]


def _symbol_cache(request: Request) -> _SymbolCache:
    raw: Any = getattr(request.app.state, "market_symbols_cache", None)
    if raw is None:
        raw = _SymbolCache(expires_monotonic=0.0, symbols=[], top_by_volume=[])
        request.app.state.market_symbols_cache = raw
    elif "top_by_volume" not in raw:
        raw["top_by_volume"] = []
    return raw  # type: ignore[return-value]

router = APIRouter()


@router.get("/market/symbols")
async def market_symbols(
    request: Request,
    gate: GateDep,
    q: str | None = None,
    refresh: bool = False,
):
    """List Binance USDT spot trading pairs, with optional case-insensitive substring filter."""
    http = request.app.state.http
    cache = _symbol_cache(request)
    now = time.monotonic()
    if refresh or now >= cache["expires_monotonic"] or not cache["symbols"]:
        await gate.acquire()
        symbols = await fetch_usdt_spot_symbols(http)
        top: list[str] = []
        try:
            await gate.acquire()
            tickers = await fetch_ticker_24hr_all(http)
            top = top_usdt_pairs_by_quote_volume(symbols, tickers, limit=100)
        except BinanceClientError:
            top = []
        cache["symbols"] = symbols
        cache["top_by_volume"] = top
        cache["expires_monotonic"] = now + SYMBOL_CACHE_TTL_S
    out = list(cache["symbols"])
    if q is not None and q.strip():
        qu = q.strip().upper()
        out = [s for s in out if qu in s.upper()]
    return {"symbols": out, "top_by_volume": list(cache["top_by_volume"])}


def _candle_to_json(c: dict) -> dict:
    return {
        "time": int(c["open_time_ms"]),
        "open": float(c["open"]),
        "high": float(c["high"]),
        "low": float(c["low"]),
        "close": float(c["close"]),
        "volume": float(c["volume"]),
    }


@router.get("/market/history")
async def market_history(
    request: Request,
    store: StoreDep,
    settings: SettingsDep,
    gate: GateDep,
    symbol: str = "BTC/USDT",
    interval: str = "1m",
    limit: int = 200,
):
    http = request.app.state.http
    candles = await load_klines_for_dashboard(
        store,
        http,
        gate,
        symbol=symbol,
        interval=interval,
        limit=min(max(limit, 1), 1000),
    )
    return {"symbol": symbol, "interval": interval, "candles": [_candle_to_json(c) for c in candles]}


@router.get("/market/stream")
async def market_stream(
    request: Request,
    store: StoreDep,
    settings: SettingsDep,
    gate: GateDep,
    symbol: str = "BTC/USDT",
    interval: str = "1m",
):
    http = request.app.state.http

    async def gen() -> AsyncIterator[bytes]:
        backoff = 1.0
        while True:
            if await request.is_disconnected():
                break
            try:
                candles = await load_klines_for_dashboard(
                    store,
                    http,
                    gate,
                    symbol=symbol,
                    interval=interval,
                    limit=2,
                )
                backoff = 1.0
                payload = {"candles": [_candle_to_json(c) for c in candles]}
                yield f"data: {json.dumps(payload)}\n\n".encode()
            except Exception:
                yield f"data: {json.dumps({'error': True, 'retry_s': backoff})}\n\n".encode()
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 60.0)
            await asyncio.sleep(settings.live_poll_interval_s)

    return StreamingResponse(gen(), media_type="text/event-stream")
