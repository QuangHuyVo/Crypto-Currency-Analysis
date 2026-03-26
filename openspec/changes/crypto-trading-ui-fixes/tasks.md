## 1. Backend top-by-volume

- [x] 1.1 Fetch `/api/v3/ticker/24hr`, intersect eligible USDT spot symbols, return top 100 by `quoteVolume` in `GET /market/symbols` as `top_by_volume`
- [x] 1.2 Extend cache + tests

## 2. Frontend

- [x] 2.1 Layout: `100vh` column + `minHeight: 0` on chart flex child
- [x] 2.2 Rebrand: Crypto Trading (`App`, `index.html`, tests)
- [x] 2.3 `CandleVolumeChart` supports `chartType` candle | line; crosshair OHLC from bar lookup in line mode
- [x] 2.4 Symbol search: show `top_by_volume` when query empty
- [x] 2.5 Run pytest + `npm run build` + `npm run test`
