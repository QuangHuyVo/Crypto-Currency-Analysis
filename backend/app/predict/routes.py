from __future__ import annotations

import pandas as pd
from fastapi import APIRouter

from app.deps import SettingsDep, StoreDep
from app.ml.infer import DISCLAIMER, try_predict

router = APIRouter()


@router.get("/predict")
async def predict(
    store: StoreDep,
    settings: SettingsDep,
    symbol: str = "BTC/USDT",
    interval: str = "1m",
):
    rows = await store.list_candles(symbol, interval, limit=1000)
    df = pd.DataFrame(rows)
    if df.empty:
        return {
            "available": False,
            "reason": "insufficient_data",
            "disclaimer": DISCLAIMER,
            "symbol": symbol,
            "interval": interval,
        }
    for col in ("open", "high", "low", "close", "volume"):
        if col not in df.columns:
            return {
                "available": False,
                "reason": "insufficient_data",
                "disclaimer": DISCLAIMER,
                "symbol": symbol,
                "interval": interval,
            }
    return try_predict(settings.models_dir, symbol, interval, df)
