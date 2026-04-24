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


def ingest_spy_candles(
    provider: str | None = None,
    csv_path: str | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str | None = None,
):
    settings = get_settings()
    source_provider = (provider or settings.candles_provider).lower()
    client = MarketDataClient()

    candles = client.load_spy_candles(
        provider=source_provider,
        symbol=settings.default_symbol,
        timeframe=timeframe or settings.default_timeframe,
        csv_path=csv_path or settings.spy_candles_csv_path,
        start=start,
        end=end,
        alpaca_api_key=settings.alpaca_api_key,
        alpaca_secret_key=settings.alpaca_secret_key,
        alpaca_data_base_url=settings.alpaca_data_base_url,
    )
    deduped = dedupe_candles(candles)
    audit = IngestionAudit(source=source_provider, loaded_at=UTC_NOW(), records_in=len(candles), records_out=len(deduped))
    return deduped, audit


def ingest_options_snapshot(payload: list[dict], provider: str = "internal"):
    client = OptionsChainClient()
    snapshots = client.normalize_snapshot(payload=payload, provider=provider)
    deduped = dedupe_option_snapshots(snapshots)
    audit = IngestionAudit(source=provider, loaded_at=UTC_NOW(), records_in=len(snapshots), records_out=len(deduped))
    return deduped, audit
