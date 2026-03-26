# Design: TradingView Tier A

## Architecture

```
Browser                    FastAPI
  │                           │
  ├── GET /api/market/symbols ──► exchangeInfo (cached ~1h) → base/USDT list
  ├── GET /api/market/history ──► existing klines path
  └── GET /api/predict       ──► unchanged

Frontend: `lightweight-charts` (v4) single chart — candlestick series + histogram
(volume), shared time scale. Crosshair subscription updates a small legend strip.

## Theming

Netflix-adjacent dark shell: near-black `#0a0a0a`, panels `#141414`, accent `#e50914`
for focus (interval active, links). Chart grid matches shell.

## URL state

`symbol` and `interval` query params; `replaceState` on change so refresh shares view.

## Keyboard

Digits `1`–`4` map to `1m`, `5m`, `15m`, `1h`. Ignored when focus is in an input.

## Testing

- Backend: mock `exchangeInfo` for `/market/symbols`
- Frontend: mock `fetch` for symbols + history + predict; smoke test for heading / interval buttons
