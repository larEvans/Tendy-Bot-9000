"""MVP ingestion jobs and dedup helpers for milestone 2."""

from __future__ import annotations

from app.core.config import get_settings
from app.db.models import IngestionAudit, OptionsChainSnapshot, UTC_NOW
from app.ingestion.market_data_client import MarketDataClient
from app.ingestion.options_chain_client import OptionsChainClient


def dedupe_candles(candles):
    unique = {(c.symbol, c.timeframe, c.timestamp): c for c in candles}
    return list(unique.values())


def dedupe_option_snapshots(snapshots: list[OptionsChainSnapshot]) -> list[OptionsChainSnapshot]:
    unique = {(s.option_symbol, s.snapshot_time): s for s in snapshots}
    return list(unique.values())


def ingest_spy_candles(csv_path: str | None = None):
    settings = get_settings()
    source = csv_path or settings.spy_candles_csv_path
    client = MarketDataClient()
    candles = client.load_candles(source, symbol=settings.default_symbol, timeframe=settings.default_timeframe)
    deduped = dedupe_candles(candles)
    audit = IngestionAudit(source=source, loaded_at=UTC_NOW(), records_in=len(candles), records_out=len(deduped))
    return deduped, audit


def ingest_options_snapshot(payload: list[dict]):
    client = OptionsChainClient()
    snapshots = client.normalize_snapshot(payload)
    deduped = dedupe_option_snapshots(snapshots)
    audit = IngestionAudit(source="options_payload", loaded_at=UTC_NOW(), records_in=len(snapshots), records_out=len(deduped))
    return deduped, audit
