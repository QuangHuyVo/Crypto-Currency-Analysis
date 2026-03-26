from __future__ import annotations

from typing import Any

import httpx

from app.binance.klines import BinanceClientError, to_binance_symbol


async def fetch_ticker_24hr_all(client: httpx.AsyncClient) -> list[dict[str, Any]]:
    r = await client.get("/api/v3/ticker/24hr")
    if r.status_code >= 400:
        try:
            body = r.json()
            msg = str(body.get("msg", r.text))
        except Exception:
            msg = r.text
        raise BinanceClientError(msg, status_code=r.status_code)
    data = r.json()
    if not isinstance(data, list):
        raise BinanceClientError("Unexpected ticker/24hr response shape", status_code=r.status_code)
    return data


def top_usdt_pairs_by_quote_volume(
    symbols_slash: list[str],
    tickers: list[dict[str, Any]],
    *,
    limit: int = 100,
) -> list[str]:
    binance_to_slash = {to_binance_symbol(s): s for s in symbols_slash}
    eligible = set(binance_to_slash.keys())
    ranked: list[tuple[float, str]] = []
    for t in tickers:
        if not isinstance(t, dict):
            continue
        sym = t.get("symbol")
        if not isinstance(sym, str) or sym not in eligible:
            continue
        try:
            qv = float(t.get("quoteVolume", 0) or 0)
        except (TypeError, ValueError):
            continue
        ranked.append((qv, sym))
    ranked.sort(key=lambda x: -x[0])
    out: list[str] = []
    seen: set[str] = set()
    for _, bsym in ranked:
        sl = binance_to_slash.get(bsym)
        if sl and sl not in seen:
            seen.add(sl)
            out.append(sl)
        if len(out) >= limit:
            break
    return out
