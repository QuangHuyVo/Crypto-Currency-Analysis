# Proposal: TradingView Tier A (chart + symbols + layout)

## Summary

Deliver **Tier A** from the dashboard roadmap: real OHLC candlesticks with volume, crosshair OHLC readout, interval toolbar, searchable USDT spot symbols (Binance-backed), full-viewport chart layout, URL sync for symbol/interval, and basic keyboard shortcuts (1–4 for timeframe).

## Non-goals (this change)

- Pattern library (`candlestick` npm) integration
- Python ML / feature changes
- Drawing tools, extra indicators (Tier B)
- Netflix-style motion / row carousels (only dark “cinema” shell colors)

## Success criteria

- History API unchanged for clients; new `GET /market/symbols` for USDT spot list with optional `q` filter and server-side cache.
- Chart shows candles + volume; crosshair shows O/H/L/C (+ volume when over bar).
- Symbol picker searchable; intervals as buttons; `?symbol=&interval=` round-trip; keys 1–4 switch interval when not typing in search.
