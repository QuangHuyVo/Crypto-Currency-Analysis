from __future__ import annotations

import pandas as pd

# Rolling window 5 + lags 3 + warmup; keep explicit minimum for callers
MIN_ROWS_FOR_FEATURES = 32


def build_feature_matrix(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    """Build X, y (next-bar up direction), and aligned open_time_ms index."""
    if len(df) < MIN_ROWS_FOR_FEATURES + 2:
        raise ValueError("insufficient data: not enough rows for features and target")

    d = df.sort_values("open_time_ms").reset_index(drop=True)
    c = d["close"].astype(float)
    ret = c.pct_change()

    feat = pd.DataFrame(
        {
            "return_lag_1": ret.shift(1),
            "return_lag_2": ret.shift(2),
            "return_lag_3": ret.shift(3),
            "vol_roll_5": ret.rolling(5).std().shift(1),
            "close_roll_mean_5": c.rolling(5).mean().pct_change().shift(1),
        }
    )
    y = (c.shift(-1) > c).astype(float)
    mask = feat.notna().all(axis=1) & y.notna()
    X = feat.loc[mask].reset_index(drop=True)
    y = y.loc[mask].reset_index(drop=True).astype(int)
    idx = d.loc[mask, "open_time_ms"].reset_index(drop=True)
    return X, y, idx
