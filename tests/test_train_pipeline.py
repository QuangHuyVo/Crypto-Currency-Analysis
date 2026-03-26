"""Training saves artifacts (task 3.2)."""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestClassifier

from app.ml.features import build_feature_matrix
from app.ml.train import train_and_save


def test_train_and_save_writes_model_and_metadata(tmp_path: Path):
    rng = np.random.default_rng(0)
    n = 120
    base = 100 + np.cumsum(rng.normal(0, 0.5, size=n))
    df = pd.DataFrame(
        {
            "open_time_ms": np.arange(n, dtype=np.int64) * 60_000,
            "open": base,
            "high": base + 0.2,
            "low": base - 0.2,
            "close": base,
            "volume": rng.random(n) * 10,
        }
    )
    out = tmp_path / "m"
    metrics = train_and_save(df, out, symbol="BTC/USDT", interval="1m", model_cls=RandomForestClassifier)
    assert metrics["val_accuracy"] >= 0
    assert (out / "model.joblib").is_file()
    assert (out / "metadata.json").is_file()
    loaded = joblib.load(out / "model.joblib")
    assert isinstance(loaded, RandomForestClassifier)
    X, _, _ = build_feature_matrix(df)
    p = loaded.predict(X.tail(1))
    assert p.shape == (1,)
