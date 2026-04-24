"""Historical OHLCV ingestion from CSV-like sources."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from app.db.models import MarketCandle


class MarketDataClient:
    """Loads normalized OHLCV candles from local CSV files."""

    def load_candles(self, csv_path: str, symbol: str, timeframe: str) -> list[MarketCandle]:
        rows = list(self._read_rows(csv_path))
        candles: list[MarketCandle] = []
        for row in rows:
            candles.append(
                MarketCandle(
                    symbol=symbol,
                    timeframe=timeframe,
                    timestamp=datetime.strptime(row["Date"], "%Y-%m-%d").replace(tzinfo=timezone.utc),
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    volume=int(float(row["Volume"])),
                )
            )
        return candles

    def _read_rows(self, csv_path: str) -> Iterable[dict[str, str]]:
        path = Path(csv_path)
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            yield from reader
