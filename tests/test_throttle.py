"""Outbound REST spacing (task 5.1)."""

import asyncio
import time

import pytest

from app.binance.throttle import AsyncMinIntervalGate


@pytest.mark.asyncio
async def test_gate_enforces_minimum_spacing():
    gate = AsyncMinIntervalGate(min_interval_s=0.05)
    t0 = time.perf_counter()
    await gate.acquire()
    await gate.acquire()
    elapsed = time.perf_counter() - t0
    assert elapsed >= 0.05
