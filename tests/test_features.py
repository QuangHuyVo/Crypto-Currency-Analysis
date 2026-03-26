"""ML feature builder (task 3.1)."""

import pandas as pd
import pytest

from app.ml.features import MIN_ROWS_FOR_FEATURES, build_feature_matrix


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
