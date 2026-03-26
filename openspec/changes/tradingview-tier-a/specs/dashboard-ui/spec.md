# Spec: Dashboard UI (Tier A extension)

## Requirements

1. **Candles + volume**: The primary chart SHALL display OHLC candlesticks and a volume histogram aligned on the same time axis.
2. **Crosshair**: Moving the crosshair SHALL show human-readable O, H, L, C and volume for the active bar when available.
3. **Symbol discovery**: The user SHALL search Binance USDT spot symbols via backend-backed list (not a fixed trio only).
4. **Timeframes**: Intervals SHALL be selectable via visible buttons; optional keyboard shortcuts 1–4 for the four default intervals.
5. **Layout**: The chart area SHALL use the main viewport height (scroll only for auxiliary panels if needed).
6. **Shareable state**: Symbol and interval SHALL be reflected in the URL query string.

## Out of scope

- Indicator overlays, drawings, alerts, pattern detection (later changes).
