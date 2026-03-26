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


def build_inference_row_at_open_time(
    df: pd.DataFrame,
    as_of_open_time_ms: int,
) -> tuple[pd.DataFrame, int]:
    """Feature row for the bar at ``as_of_open_time_ms`` using only candles with open <= as-of.

    Unlike :func:`build_feature_matrix`, does not require the next bar's close (inference only).
    """
    if df.empty:
        raise ValueError("insufficient data: empty candle frame")
    d = df.sort_values("open_time_ms").reset_index(drop=True)
    times = d["open_time_ms"].astype(int)
    if int(as_of_open_time_ms) not in set(times.tolist()):
        raise ValueError("as_of bar not in series")
    d = d.loc[times <= int(as_of_open_time_ms)].reset_index(drop=True)
    if len(d) < MIN_ROWS_FOR_FEATURES:
        raise ValueError("insufficient data: not enough rows before as_of for features")

    pos = int(d.index[d["open_time_ms"].astype(int) == int(as_of_open_time_ms)].max())
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
    row = feat.iloc[[pos]]
    if not row.notna().all(axis=1).all():
        raise ValueError("insufficient data: features not warm at as_of bar")
    bar_ts = int(d.iloc[pos]["open_time_ms"])
    return row, bar_ts
