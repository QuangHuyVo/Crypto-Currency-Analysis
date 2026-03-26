# Crypto Currency Analysis

Binance market data + charting dashboard with optional ML predictions (FastAPI backend, React + Vite frontend).

## Prerequisites

- **Python 3.11+**
- **Node.js** (for the frontend dev server)

## Run the app (development)

You need **two terminals**: API on port **8000**, UI on port **5173** (Vite proxies `/api` to the backend).

### 1. Backend

From the **repository root** (the folder that contains `pyproject.toml`):

```bash
python -m pip install -e ".[dev]"
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Use **`python -m uvicorn`** so you do not rely on the `uvicorn.exe` entry point being on your PATH (common on Windows). If you use a virtual environment, activate it first, then run the same commands.

**PowerShell (optional venv):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in the browser.

## Environment variables (optional)

| Variable | Default | Purpose |
|----------|---------|---------|
| `DATABASE_PATH` | `data/candles.db` | SQLite candle cache |
| `MODELS_DIR` | `models` | Trained model artifacts for `/predict` |
| `CORS_ORIGINS` | `*` | CORS allowed origins |
| `BINANCE_REST_BASE` | `https://api.binance.com` | REST API base |
| `BINANCE_MIN_INTERVAL_MS` | `200` | Min delay between outbound REST calls |
| `LIVE_POLL_INTERVAL_S` | `5` | Polling interval for live updates |

Without models under `MODELS_DIR`, prediction endpoints may return “no model” / unavailable until you train (see `train-model --help` after install).

## Tests

From the repository root:

```bash
python -m pip install -e ".[dev]"
python -m pytest
cd frontend && npm test
```

## OpenSpec (specs & changes)

Product specs live under `openspec/specs/`. Completed change folders may be archived under `openspec/changes/archive/`. Use your project’s OpenSpec / Cursor commands (`propose`, `apply`, `archive`) as documented there.
