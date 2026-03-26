from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

Candle = dict[str, float | int]


class BinanceClientError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def to_binance_symbol(symbol: str) -> str:
    s = symbol.strip().upper()
    if "/" in s:
        base, quote = s.split("/", 1)
        return f"{base}{quote}"
    return s


def parse_klines_json(raw: list[list[Any]]) -> list[Candle]:
    out: list[Candle] = []
    for row in raw:
        out.append(
            {
                "open_time_ms": int(row[0]),
                "open": float(row[1]),
                "high": float(row[2]),
                "low": float(row[3]),
                "close": float(row[4]),
                "volume": float(row[5]),
            }
        )
    return out


async def fetch_klines(
    client: httpx.AsyncClient,
    symbol: str,
    interval: str,
    *,
    limit: int = 500,
) -> list[Candle]:
    sym = to_binance_symbol(symbol)
    params = {"symbol": sym, "interval": interval, "limit": limit}
    logger.info("Binance REST klines symbol=%s interval=%s limit=%s", sym, interval, limit)
    r = await client.get("/api/v3/klines", params=params)
    if r.status_code >= 400:
        try:
            body = r.json()
            msg = str(body.get("msg", r.text))
        except Exception:
            msg = r.text
        raise BinanceClientError(msg, status_code=r.status_code)
    data = r.json()
    if not isinstance(data, list):
        raise BinanceClientError("Unexpected klines response shape", status_code=r.status_code)
    return parse_klines_json(data)
