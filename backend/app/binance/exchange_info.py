from __future__ import annotations

from typing import Any

import httpx

from app.binance.klines import BinanceClientError


def _normalize_usdt_pair(s: dict[str, Any]) -> str | None:
    if s.get("quoteAsset") != "USDT":
        return None
    if s.get("status") != "TRADING":
        return None
    perms = s.get("permissions")
    if isinstance(perms, list) and perms and "SPOT" not in perms:
        return None
    base = s.get("baseAsset")
    if not base or not isinstance(base, str):
        return None
    return f"{base}/USDT"


def parse_exchange_info_symbols(raw: dict[str, Any]) -> list[str]:
    symbols: list[str] = []
    for s in raw.get("symbols", []):
        if not isinstance(s, dict):
            continue
        p = _normalize_usdt_pair(s)
        if p:
            symbols.append(p)
    return sorted(set(symbols))


async def fetch_usdt_spot_symbols(client: httpx.AsyncClient) -> list[str]:
    r = await client.get("/api/v3/exchangeInfo")
    if r.status_code >= 400:
        try:
            body = r.json()
            msg = str(body.get("msg", r.text))
        except Exception:
            msg = r.text
        raise BinanceClientError(msg, status_code=r.status_code)
    data = r.json()
    if not isinstance(data, dict):
        raise BinanceClientError("Unexpected exchangeInfo shape", status_code=r.status_code)
    return parse_exchange_info_symbols(data)
