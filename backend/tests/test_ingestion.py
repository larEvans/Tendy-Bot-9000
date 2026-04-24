from __future__ import annotations

from datetime import datetime, timezone

from app.ingestion.jobs import dedupe_candles, dedupe_option_snapshots
from app.ingestion.market_data_client import MarketDataClient
from app.ingestion.options_chain_client import OptionsChainClient


def test_market_data_client_loads_candles():
    client = MarketDataClient()
    candles = client.load_candles("backend/fixtures/spy_candles_fixture.csv", symbol="SPY", timeframe="15m")
    assert len(candles) == 2
    assert candles[0].symbol == "SPY"
    assert candles[0].timeframe == "15m"


def test_dedupe_candles_by_symbol_timeframe_timestamp():
    client = MarketDataClient()
    candles = client.load_candles("backend/fixtures/spy_candles_fixture.csv", symbol="SPY", timeframe="15m")
    duplicated = candles + [candles[0]]
    deduped = dedupe_candles(duplicated)
    assert len(deduped) == 2


def test_options_normalization_and_deduplication():
    payload = [
        {
            "underlying": "SPY",
            "option_symbol": "SPY250117C00550000",
            "expiration_date": "2025-01-17",
            "strike": 550,
            "option_type": "call",
            "bid": 2.1,
            "ask": 2.3,
            "last_price": 2.2,
            "volume": 1500,
            "open_interest": 3100,
        }
    ]

    client = OptionsChainClient()
    ts = datetime(2026, 4, 24, 14, 30, tzinfo=timezone.utc)
    snapshots = client.normalize_snapshot(payload, snapshot_time=ts)
    duplicated = snapshots + [snapshots[0]]
    deduped = dedupe_option_snapshots(duplicated)

    assert len(snapshots) == 1
    assert round(snapshots[0].mid, 4) == 2.2
    assert len(deduped) == 1
