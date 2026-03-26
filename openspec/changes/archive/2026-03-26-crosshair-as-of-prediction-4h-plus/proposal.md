## Why

The dashboard currently treats ML inference as “as of the latest closed bar,” which does not match how users analyze history: they often want a forecast conditioned on the bar under inspection. Defining “current point” as **the bar under the crosshair at click** gives a clear, reproducible anchor and avoids ambiguous “in-progress bar” semantics, while scoping to **4h and higher** intervals keeps the product aligned with slower strategic timeframes and existing data expectations.

## What Changes

- **prediction anchor**: Prediction requests SHALL be driven by an explicit **as-of bar** chosen by the user via chart interaction (bar under crosshair when the user commits the action, e.g. click), not implicitly “last bar in series.”
- **timeframe gate**: As-of prediction is enabled only for intervals **4h, 1d, 1w, 1M** (and any future interval the product classifies as “long-horizon”); shorter intervals show a clear disabled or explanatory state.
- **API contract**: Prediction endpoint (or equivalent) accepts an **as-of timestamp** (or bar open time) plus symbol and interval; the backend builds features using **only** candles through that bar’s close—**no lookahead** from later bars.
- **UI**: Prediction panel shows which bar was used (timestamp aligned to interval), and updates when the user selects a new anchor; idle state explains how to pick a bar (click on chart with crosshair).
- **disclaimers**: Existing experimental / non-advisory labeling for ML output remains in force.

## Capabilities

### New Capabilities

- `crosshair-as-of-prediction`: User interaction, gating by interval, and API/UI contract for running inference as of the bar under the crosshair at click, including error states (insufficient history, unsupported interval).

### Modified Capabilities

- `ml-price-forecast`: Extend serving predictions from “latest feature row only” to “feature row aligned to a supplied as-of bar,” preserving no-leakage rules and versioned model metadata.
- `dashboard-ui`: Bind prediction panel to the crosshair-click anchor where supported; show as-of bar context and limitation notice consistent with ML spec.

## Impact

- **Frontend**: Chart/crosshair click handling, interval checks, prediction request payload, prediction panel display for anchored bar.
- **Backend**: Prediction route or service accepts `as_of` / bar key; feature pipeline truncates history at that bar; validation for supported intervals and minimum history.
- **Tests**: API tests for as-of inference, truncation/lookahead; UI tests or integration checks for 4h+ vs blocked intervals.
- **Dependencies**: None beyond existing candle storage and ML stack; no **BREAKING** change if legacy “latest bar” remains as default when as-of omitted (design will confirm).
