from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    binance_rest_base: str
    database_path: Path
    models_dir: Path
    cors_origins: list[str]
    binance_min_interval_ms: float
    live_poll_interval_s: float


def load_settings() -> Settings:
    cors = os.environ.get("CORS_ORIGINS", "*")
    origins = ["*"] if cors.strip() == "*" else [x.strip() for x in cors.split(",") if x.strip()]
    return Settings(
        binance_rest_base=os.environ.get("BINANCE_REST_BASE", "https://api.binance.com").rstrip("/"),
        database_path=Path(os.environ.get("DATABASE_PATH", "data/candles.db")),
        models_dir=Path(os.environ.get("MODELS_DIR", "models")),
        cors_origins=origins,
        binance_min_interval_ms=float(os.environ.get("BINANCE_MIN_INTERVAL_MS", "200")),
        live_poll_interval_s=float(os.environ.get("LIVE_POLL_INTERVAL_S", "5")),
    )
