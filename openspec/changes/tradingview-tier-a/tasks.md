## 1. Market symbols API

- [x] 1.1 Add Binance `exchangeInfo` client helper and `GET /market/symbols` with optional `q`, in-memory cache (~1h) on `app.state`
- [x] 1.2 Unit test with mocked HTTP response for symbol list

## 2. Frontend chart and layout

- [x] 2.1 Add `lightweight-charts` candlestick + volume component with crosshair OHLC(+V) legend
- [x] 2.2 Full-viewport layout and Netflix-style dark theme (shell + toolbar)
- [x] 2.3 Symbol search combobox fed by `/market/symbols`; interval button group; URL query sync
- [x] 2.4 Keyboard shortcuts 1–4 for intervals (documented in UI)
- [x] 2.5 Remove Recharts `PriceChart`; update frontend tests and dependencies
