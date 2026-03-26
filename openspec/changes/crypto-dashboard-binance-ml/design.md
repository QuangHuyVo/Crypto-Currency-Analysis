## Context

The change is greenfield: an interactive crypto dashboard backed by Binance public market data and an ML price-forecast layer. Stakeholders need live charts, reliable ingestion under rate limits, and predictions that are clearly labeled as experimental—not trading signals. The proposal defines three capabilities: `binance-market-data`, `ml-price-forecast`, and `dashboard-ui`.

## Goals / Non-Goals

**Goals:**

- Ingest OHLCV (and optionally trades/ticker) from Binance public APIs with reconnect and backoff.
- Train and run a documented baseline model (e.g., gradient boosting or simple sequence model) on rolling windows; expose predictions via an internal API.
- Deliver a dashboard with symbol/timeframe selection, live or near-live charts, prediction panel, and visible data staleness/errors.

**Non-Goals:**

- Order placement, account balances, or any authenticated trading on Binance.
- Guaranteed profitable forecasts or regulatory/compliance sign-off for financial advice.
- Multi-exchange aggregation in v1.
- HPC-scale training or sub-second WebSocket fan-out to many clients (single-user / small team scope first).

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| App shape | **Python backend (FastAPI) + web frontend (React + Vite)** | Clear split: async I/O and ML in Python; rich interactivity in the browser. Alternative **Streamlit** was rejected for v1 product shape to avoid coupling UI and long-running jobs in one process; can add a Streamlit prototype later if needed. |
| Binance access | **Native REST + WebSocket** (e.g., `httpx` / `websockets`, or `ccxt` for normalization) | Public endpoints only; `ccxt` reduces exchange-specific quirks if we add exchanges later. |
| Storage | **SQLite** (or Parquet on disk) for candles cache; optional **Redis** later for pub/sub | SQLite keeps MVP simple; sufficient for single-machine cache and experiment metadata. |
| ML stack | **scikit-learn** or **XGBoost** for tabular baseline; optional **PyTorch** only if sequence model is required | Faster iteration and smaller ops surface than deep learning by default. |
| Features | Lags of returns, rolling mean/vol, simple technical aggregates aligned to bar interval | Interpretable and cheap to compute live. |
| Model lifecycle | Versioned **artifact files** (pickle/joblib + metadata JSON) under `models/`; training as a **CLI script** invoked manually or on schedule | Avoids premature MLOps complexity; tasks.md can add automation. |
| Real-time UX | Backend holds WebSocket to Binance (or polls REST at safe interval); **Server-Sent Events or WebSocket** from API to browser | Keeps API keys (if ever needed) off the client; centralizes rate limiting. |
| Deployment | **Docker Compose** optional; local `uv`/`pip` + `npm` dev scripts documented | Matches small-team workflow. |

## Risks / Trade-offs

- **[Risk] Binance API changes or geo-blocking** → Mitigation: abstract provider behind an interface; surface clear errors in UI; document VPN/legal constraints for operators.
- **[Risk] ML overfitting / misleading users** → Mitigation: show train window, metrics on holdout, disclaimer; default to conservative horizons.
- **[Risk] Rate limits under many symbols** → Mitigation: throttle subscriptions; cache klines; single active symbol default in UI.
- **[Risk] WebSocket disconnects** → Mitigation: exponential backoff, snapshot + resync from REST klines.

## Migration Plan

Not applicable (new codebase). **Rollout:** land backend → data pipeline smoke tests → frontend → enable dashboard in README. **Rollback:** disable prediction endpoint and show data-only dashboard via feature flag or config.

## Open Questions

- Exact default **symbols** and **bar interval** (e.g., BTCUSDT / 1m).
- Whether v1 ships **WebSocket** from Binance or **REST polling** only (polling is simpler; WebSocket is more “real-time”).
- Target **prediction horizon** (e.g., next 1 bar vs. next 5 bars) and classification vs. regression.
