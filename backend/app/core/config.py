"""Application configuration for ingestion jobs."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    default_symbol: str = os.getenv("DEFAULT_SYMBOL", "SPY")
    default_timeframe: str = os.getenv("DEFAULT_TIMEFRAME", "1d")
    candles_provider: str = os.getenv("CANDLES_PROVIDER", "yfinance")
    options_provider: str = os.getenv("OPTIONS_PROVIDER", "yfinance")

    spy_candles_csv_path: str = os.getenv("SPY_CANDLES_CSV_PATH", "backend/fixtures/spy_candles_fixture.csv")

    alpaca_data_base_url: str = os.getenv("ALPACA_DATA_BASE_URL", "https://data.alpaca.markets")
    alpaca_api_key: str = os.getenv("ALPACA_API_KEY", "")
    alpaca_secret_key: str = os.getenv("ALPACA_SECRET_KEY", "")


def get_settings() -> Settings:
    return Settings()
