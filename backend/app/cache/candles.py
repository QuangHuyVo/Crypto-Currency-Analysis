from __future__ import annotations

from pathlib import Path
from typing import Any

import aiosqlite

from app.binance.klines import Candle, to_binance_symbol


def _key_symbol(symbol: str) -> str:
    return to_binance_symbol(symbol)


class CandleStore:
    def __init__(self, db_path: Path):
        self._path = db_path

    async def init(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self._path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS candles (
                    symbol TEXT NOT NULL,
                    interval TEXT NOT NULL,
                    open_time_ms INTEGER NOT NULL,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume REAL NOT NULL,
                    PRIMARY KEY (symbol, interval, open_time_ms)
                )
                """
            )
            await db.commit()

    async def upsert_candles(self, symbol: str, interval: str, candles: list[Candle]) -> None:
        if not candles:
            return
        sym = _key_symbol(symbol)
        rows = [
            (
                sym,
                interval,
                int(c["open_time_ms"]),
                float(c["open"]),
                float(c["high"]),
                float(c["low"]),
                float(c["close"]),
                float(c["volume"]),
            )
            for c in candles
        ]
        async with aiosqlite.connect(self._path) as db:
            await db.executemany(
                """
                INSERT INTO candles (symbol, interval, open_time_ms, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(symbol, interval, open_time_ms) DO UPDATE SET
                    open=excluded.open,
                    high=excluded.high,
                    low=excluded.low,
                    close=excluded.close,
                    volume=excluded.volume
                """,
                rows,
            )
            await db.commit()

    async def list_candles(self, symbol: str, interval: str, *, limit: int) -> list[dict[str, Any]]:
        sym = _key_symbol(symbol)
        async with aiosqlite.connect(self._path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
                """
                SELECT open_time_ms, open, high, low, close, volume
                FROM (
                    SELECT open_time_ms, open, high, low, close, volume
                    FROM candles
                    WHERE symbol = ? AND interval = ?
                    ORDER BY open_time_ms DESC
                    LIMIT ?
                )
                ORDER BY open_time_ms ASC
                """,
                (sym, interval, limit),
            )
            rows = await cur.fetchall()
        return [dict(r) for r in rows]
