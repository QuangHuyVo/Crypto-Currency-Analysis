from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from app.ml.features import build_feature_matrix
from app.ml.train import model_dir_for

DISCLAIMER = (
    "Experimental machine-learning output for exploration only. "
    "Not financial advice. Past performance does not guarantee future results."
)


def try_predict(
    models_dir: Path,
    symbol: str,
    interval: str,
    df: pd.DataFrame,
) -> dict[str, Any]:
    bundle = model_dir_for(models_dir, symbol, interval)
    model_path = bundle / "model.joblib"
    meta_path = bundle / "metadata.json"
    base = {
        "available": False,
        "disclaimer": DISCLAIMER,
        "symbol": symbol,
        "interval": interval,
    }
    if not model_path.is_file() or not meta_path.is_file():
        return {**base, "reason": "no_model"}

    try:
        X, _, idx = build_feature_matrix(df)
    except ValueError as e:
        return {**base, "reason": "insufficient_data", "detail": str(e)}

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    cols = meta.get("feature_columns") or list(X.columns)
    model = joblib.load(model_path)
    row = X.iloc[[-1]]
    for c in cols:
        if c not in row.columns:
            return {**base, "reason": "feature_mismatch", "detail": c}
    p = int(model.predict(row[cols])[0])
    last_ts = int(idx.iloc[-1])
    return {
        "available": True,
        "prediction_class": p,
        "prediction_label": "next_close_up" if p == 1 else "next_close_not_up",
        "last_bar_time_ms": last_ts,
        "model_version": meta.get("version"),
        "metrics": meta.get("metrics"),
        "disclaimer": DISCLAIMER,
        "symbol": symbol,
        "interval": interval,
    }
