from __future__ import annotations

# Intervals allowed for crosshair / as-of prediction (must stay in sync with dashboard policy).
AS_OF_PREDICTION_INTERVALS: frozenset[str] = frozenset({"4h", "1d", "1w", "1M"})
