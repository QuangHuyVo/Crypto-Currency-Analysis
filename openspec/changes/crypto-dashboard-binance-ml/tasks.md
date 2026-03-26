## 1. Repository and runtime setup



- [x] 1.1 Initialize Python project (e.g., `pyproject.toml` or `requirements.txt`) with FastAPI, httpx, websockets or ccxt, pandas, scikit-learn (or XGBoost), and dev tools

- [x] 1.2 Initialize frontend (React + Vite) with charting library (e.g., Lightweight Charts or Recharts) and API client

- [x] 1.3 Add README with prerequisites, env vars (if any), and how to run backend + frontend

- [x] 1.4 Optional: add `docker-compose.yml` for local API + static frontend build



## 2. Binance market data service



- [x] 2.1 Implement REST client for klines (OHLCV) with symbol/interval params, UTC normalization, and structured errors

- [x] 2.2 Implement live feed (WebSocket kline/ticker or rate-limited REST polling) with reconnect/backoff

- [x] 2.3 Add local cache (SQLite or Parquet) for recent candles and reconciliation on startup

- [x] 2.4 Expose HTTP routes: history for dashboard, internal stream or SSE/WebSocket endpoint for live updates

- [x] 2.5 Unit or integration smoke test against Binance test/public endpoints (mock in CI if needed)



## 3. ML pipeline and API



- [x] 3.1 Implement feature builder from OHLCV (lags, rolling stats) with minimum-history checks

- [x] 3.2 Implement training CLI: time-based split, metrics, save model + `metadata.json` (version, train range, feature schema)

- [x] 3.3 Implement inference path: load model, build latest feature row, return prediction + bar timestamp + version

- [x] 3.4 Add prediction route(s) wired to inference; return structured “unavailable” when no model or insufficient data

- [x] 3.5 Ensure responses/UI copy include non-advisory limitation wording



## 4. Dashboard UI



- [x] 4.1 Build symbol and interval selectors bound to API query params

- [x] 4.2 Implement candlestick/price chart with loading state and live updates from backend stream or polling

- [x] 4.3 Add prediction panel (value/class, model version, last bar time, disclaimer, empty/error states)

- [x] 4.4 Handle API failures with visible errors and safe stale-data behavior



## 5. Hardening and docs



- [x] 5.1 Add basic rate-limit/throttle configuration and logging for outbound Binance calls

- [x] 5.2 Document default symbol/interval, prediction horizon, and how to train/deploy a new model artifact

- [x] 5.3 Manual end-to-end check: select symbol → see chart → run training → see prediction update (see README “Manual end-to-end check”)


