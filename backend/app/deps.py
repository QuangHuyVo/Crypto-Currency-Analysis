from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request

from app.binance.throttle import AsyncMinIntervalGate
from app.cache.candles import CandleStore
from app.config import Settings, load_settings


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_store(request: Request) -> CandleStore:
    return request.app.state.store


def get_http(request: Request):
    return request.app.state.http


def get_gate(request: Request) -> AsyncMinIntervalGate:
    return request.app.state.gate


SettingsDep = Annotated[Settings, Depends(get_settings)]
StoreDep = Annotated[CandleStore, Depends(get_store)]
HttpDep = Depends(get_http)
GateDep = Annotated[AsyncMinIntervalGate, Depends(get_gate)]

__all__ = [
    "SettingsDep",
    "StoreDep",
    "GateDep",
    "get_settings",
    "get_store",
    "get_http",
    "get_gate",
    "load_settings",
]
