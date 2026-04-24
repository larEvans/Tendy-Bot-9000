"""Normalized in-memory models for MVP ingestion output."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class MarketCandle:
    symbol: str
    timeframe: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


@dataclass(frozen=True)
class OptionsChainSnapshot:
    underlying: str
    option_symbol: str
    snapshot_time: datetime
    expiration_date: str
    strike: float
    option_type: str
    bid: float
    ask: float
    last_price: float
    volume: int
    open_interest: int

    @property
    def mid(self) -> float:
        return round((self.bid + self.ask) / 2, 4)

    @property
    def bid_ask_spread_pct(self) -> float:
        if self.mid == 0:
            return 0.0
        return round(((self.ask - self.bid) / self.mid) * 100, 4)


@dataclass(frozen=True)
class IngestionAudit:
    source: str
    loaded_at: datetime
    records_in: int
    records_out: int


UTC_NOW = lambda: datetime.now(timezone.utc)
