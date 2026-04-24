"""Application configuration for ingestion jobs."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    spy_candles_csv_path: str = os.getenv("SPY_CANDLES_CSV_PATH", "hpq.us.txt")
    default_symbol: str = os.getenv("DEFAULT_SYMBOL", "SPY")
    default_timeframe: str = os.getenv("DEFAULT_TIMEFRAME", "1d")


def get_settings() -> Settings:
    return Settings()
