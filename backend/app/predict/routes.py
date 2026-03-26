from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from app.deps import SettingsDep, StoreDep
from app.ml.infer import DISCLAIMER, try_predict
from app.ml.policy import AS_OF_PREDICTION_INTERVALS

router = APIRouter()


def _parse_as_of_iso(value: str) -> int:
    s = value.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return int(dt.timestamp() * 1000)


@router.get("/predict")
async def predict(
    store: StoreDep,
    settings: SettingsDep,
    symbol: str = "BTC/USDT",
    interval: str = "1m",
    as_of: str | None = Query(
        default=None,
        description="Optional UTC bar open time (ISO-8601). When set, prediction uses features "
        "through that bar only; allowed only for intervals 4h, 1d, 1w, 1M. When omitted, behavior "
        "unchanged: latest training-style feature row from the most recent candles.",
    ),
):
    as_of_ms: int | None = None
    if as_of is not None and as_of.strip():
        if interval not in AS_OF_PREDICTION_INTERVALS:
            raise HTTPException(
                status_code=400,
                detail={
                    "reason": "unsupported_interval_for_as_of",
                    "message": f"as_of is only supported for {', '.join(sorted(AS_OF_PREDICTION_INTERVALS))}",
                },
            )
        try:
            as_of_ms = _parse_as_of_iso(as_of)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail={"reason": "invalid_as_of", "message": "as_of must be a valid ISO-8601 datetime"},
            ) from None

    rows = await store.list_candles(symbol, interval, limit=1000)
    df = pd.DataFrame(rows)
    if df.empty:
        return {
            "available": False,
            "reason": "insufficient_data",
            "disclaimer": DISCLAIMER,
            "symbol": symbol,
            "interval": interval,
            "prediction_anchor": "as_of" if as_of_ms is not None else "latest",
        }
    for col in ("open", "high", "low", "close", "volume"):
        if col not in df.columns:
            return {
                "available": False,
                "reason": "insufficient_data",
                "disclaimer": DISCLAIMER,
                "symbol": symbol,
                "interval": interval,
                "prediction_anchor": "as_of" if as_of_ms is not None else "latest",
            }

    if as_of_ms is not None:
        known = set(int(x) for x in df["open_time_ms"].tolist())
        if as_of_ms not in known:
            raise HTTPException(
                status_code=400,
                detail={
                    "reason": "as_of_not_in_series",
                    "message": "as_of does not match any bar open time for this symbol and interval",
                },
            )

    return try_predict(settings.models_dir, symbol, interval, df, as_of_ms=as_of_ms)
