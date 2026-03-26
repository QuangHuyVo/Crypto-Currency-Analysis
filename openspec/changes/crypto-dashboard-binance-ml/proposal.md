## Why

Traders and analysts need a single place to watch live crypto markets and explore short-horizon price direction—not just static charts, but data wired to Binance and a transparent ML layer so assumptions and limits are clear. Building this now establishes a reusable foundation for data ingestion, modeling, and an interactive UI.

## What Changes

- Add a project that ingests **real-time and recent historical** cryptocurrency data from **Binance** (public REST and/or WebSocket), with configurable symbols and timeframes.
- Add a **machine learning** pipeline that trains on historical features and serves **predictions** (e.g., next-interval direction or price) with explicit uncertainty/limitations—not financial advice.
- Add an **interactive dashboard** (web or desktop-friendly) with live charts, model outputs, and basic controls (symbol, timeframe, refresh).
- Document API keys (if any), rate limits, and operational constraints; default to **read-only** public market data where possible.

## Capabilities

### New Capabilities

- `binance-market-data`: Public Binance connectivity—symbols, klines/trades, WebSocket streams, backoff and error handling, optional local caching.
- `ml-price-forecast`: Feature engineering from OHLCV, model training and evaluation, inference API or batch scores, versioning and reproducibility basics.
- `dashboard-ui`: Interactive visualization, wiring to data and prediction services, loading/error states, responsive layout.

### Modified Capabilities

- _(none — no existing specs in `openspec/specs/` yet.)_

## Impact

- New application codebase (language/stack to be chosen in design—e.g., Python backend + web frontend, or full-stack framework).
- Runtime dependencies: HTTP/WebSocket client, ML stack (e.g., scikit-learn, PyTorch, or similar), charting library.
- External dependency on **Binance public APIs** (availability, rate limits, geographic restrictions).
- No breaking changes to existing repos—greenfield capability.
