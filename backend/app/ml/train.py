from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import httpx
import joblib
import pandas as pd
from sklearn.base import ClassifierMixin
from sklearn.ensemble import RandomForestClassifier

from app.binance.klines import parse_klines_json, to_binance_symbol
from app.binance.throttle import AsyncMinIntervalGate
from app.ml.features import build_feature_matrix


def train_and_save(
    df: pd.DataFrame,
    out_dir: Path,
    *,
    symbol: str,
    interval: str,
    model_cls: type[ClassifierMixin] = RandomForestClassifier,
) -> dict[str, Any]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    X, y, _ = build_feature_matrix(df)
    split = max(int(len(X) * 0.8), 1)
    if split >= len(X):
        raise ValueError("empty validation split — need more rows")
    X_train, X_val = X.iloc[:split], X.iloc[split:]
    y_train, y_val = y.iloc[:split], y.iloc[split:]
    model = model_cls(max_depth=5, random_state=0, n_estimators=64)
    model.fit(X_train, y_train)
    pred = model.predict(X_val)
    acc = float((pred == y_val).mean())
    joblib.dump(model, out_dir / "model.joblib")
    t_min = int(df["open_time_ms"].min())
    t_max = int(df["open_time_ms"].max())
    meta = {
        "version": "v1",
        "symbol": symbol,
        "interval": interval,
        "feature_columns": list(X.columns),
        "train_time_range_ms": [t_min, t_max],
        "metrics": {"val_accuracy": acc},
        "target": "next_bar_close_up",
    }
    (out_dir / "metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta["metrics"]


def model_dir_for(models_root: Path, symbol: str, interval: str) -> Path:
    return models_root / f"{to_binance_symbol(symbol)}_{interval}"


async def _async_main() -> None:
    p = argparse.ArgumentParser(description="Train baseline direction model on Binance OHLCV")
    p.add_argument("--symbol", default="BTC/USDT")
    p.add_argument("--interval", default="1m")
    p.add_argument("--limit", type=int, default=800)
    p.add_argument("--models-dir", type=Path, default=Path("models"))
    args = p.parse_args()
    gate = AsyncMinIntervalGate(0.2)
    async with httpx.AsyncClient(base_url="https://api.binance.com", timeout=60.0) as client:
        await gate.acquire()
        raw = await client.get(
            "/api/v3/klines",
            params={
                "symbol": to_binance_symbol(args.symbol),
                "interval": args.interval,
                "limit": args.limit,
            },
        )
        raw.raise_for_status()
        candles = parse_klines_json(raw.json())
    df = pd.DataFrame(
        {
            "open_time_ms": [c["open_time_ms"] for c in candles],
            "open": [c["open"] for c in candles],
            "high": [c["high"] for c in candles],
            "low": [c["low"] for c in candles],
            "close": [c["close"] for c in candles],
            "volume": [c["volume"] for c in candles],
        }
    )
    out = model_dir_for(args.models_dir, args.symbol, args.interval)
    metrics = train_and_save(df, out, symbol=args.symbol, interval=args.interval)
    print(json.dumps({"saved_to": str(out), "metrics": metrics}))


def main() -> None:
    import asyncio

    asyncio.run(_async_main())


if __name__ == "__main__":
    main()
