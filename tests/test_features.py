"""ML feature builder (task 3.1)."""

import pandas as pd
import pytest

from app.ml.features import MIN_ROWS_FOR_FEATURES, build_feature_matrix, build_inference_row_at_open_time


def test_build_feature_matrix_insufficient_history():
    df = pd.DataFrame(
        {
            "open_time_ms": [1, 2],
            "open": [1.0, 1.0],
            "high": [1.0, 1.0],
            "low": [1.0, 1.0],
            "close": [1.0, 1.0],
            "volume": [1.0, 1.0],
        }
    )
    with pytest.raises(ValueError, match="insufficient"):
        build_feature_matrix(df)


def test_build_feature_matrix_no_lookahead():
    n = MIN_ROWS_FOR_FEATURES + 20
    closes = list(range(n))
    df = pd.DataFrame(
        {
            "open_time_ms": list(range(n)),
            "open": [float(x) for x in closes],
            "high": [float(x) + 0.1 for x in closes],
            "low": [float(x) - 0.1 for x in closes],
            "close": [float(x) for x in closes],
            "volume": [1.0] * n,
        }
    )
    X, y, idx = build_feature_matrix(df)
    assert len(X) == len(y) == len(idx)
    assert "return_lag_1" in X.columns
    # last row target uses next close — should not appear in features as future data
    assert len(X) < n


def test_as_of_inference_matches_truncated_history():
    """Feature row at as_of must ignore candles after that bar (no lookahead)."""
    n = MIN_ROWS_FOR_FEATURES + 40
    step = 60_000
    closes = list(range(n))
    df = pd.DataFrame(
        {
            "open_time_ms": [i * step for i in range(n)],
            "open": [float(x) for x in closes],
            "high": [float(x) + 0.1 for x in closes],
            "low": [float(x) - 0.1 for x in closes],
            "close": [float(x) for x in closes],
            "volume": [1.0] * n,
        }
    )
    as_of = int(df.iloc[50]["open_time_ms"])
    row_full, ts_full = build_inference_row_at_open_time(df, as_of)
    truncated = df[df["open_time_ms"] <= as_of].copy()
    row_trunc, ts_trunc = build_inference_row_at_open_time(truncated, as_of)
    pd.testing.assert_frame_equal(row_full.reset_index(drop=True), row_trunc.reset_index(drop=True))
    assert ts_full == ts_trunc == as_of
