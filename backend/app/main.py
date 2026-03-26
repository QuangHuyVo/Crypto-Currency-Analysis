from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from app.binance.throttle import AsyncMinIntervalGate
from app.cache.candles import CandleStore
from app.config import load_settings
from app.market.routes import router as market_router
from app.predict.routes import router as predict_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(level=logging.INFO)
    settings = load_settings()
    app.state.settings = settings
    settings.models_dir.mkdir(parents=True, exist_ok=True)
    app.state.store = CandleStore(settings.database_path)
    await app.state.store.init()
    app.state.http = httpx.AsyncClient(base_url=settings.binance_rest_base, timeout=60.0)
    app.state.gate = AsyncMinIntervalGate(settings.binance_min_interval_ms / 1000.0)
    app.state.market_symbols_cache = {"expires_monotonic": 0.0, "symbols": [], "top_by_volume": []}
    logger.info(
        "Binance REST base=%s min_interval_ms=%s",
        settings.binance_rest_base,
        settings.binance_min_interval_ms,
    )
    yield
    await app.state.http.aclose()


def create_app() -> FastAPI:
    app = FastAPI(title="Crypto Dashboard API", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=".*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health():
        return {"status": "ok"}

    app.include_router(market_router)
    app.include_router(predict_router)

    static_dir = Path(__file__).resolve().parents[2] / "static"
    if static_dir.is_dir():
        app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="spa")

    return app


app = create_app()
