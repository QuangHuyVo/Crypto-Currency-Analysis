from __future__ import annotations

import asyncio
import time


class AsyncMinIntervalGate:
    """Ensures at least `min_interval_s` between consecutive `acquire` completions."""

    def __init__(self, min_interval_s: float):
        self._min = max(0.0, float(min_interval_s))
        self._lock = asyncio.Lock()
        self._last: float | None = None

    async def acquire(self) -> None:
        async with self._lock:
            now = time.monotonic()
            if self._last is not None:
                wait = self._min - (now - self._last)
                if wait > 0:
                    await asyncio.sleep(wait)
                    now = time.monotonic()
            self._last = now
