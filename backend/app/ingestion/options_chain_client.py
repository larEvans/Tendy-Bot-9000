"""Options-chain snapshot normalization utilities."""

from __future__ import annotations

from datetime import datetime, timezone

from app.db.models import OptionsChainSnapshot


class OptionsChainClient:
    """Converts provider payloads into normalized options snapshots."""

    def normalize_snapshot(self, payload: list[dict], snapshot_time: datetime | None = None) -> list[OptionsChainSnapshot]:
        when = snapshot_time or datetime.now(timezone.utc)
        results: list[OptionsChainSnapshot] = []
        for row in payload:
            results.append(
                OptionsChainSnapshot(
                    underlying=row["underlying"],
                    option_symbol=row["option_symbol"],
                    snapshot_time=when,
                    expiration_date=row["expiration_date"],
                    strike=float(row["strike"]),
                    option_type=row["option_type"],
                    bid=float(row["bid"]),
                    ask=float(row["ask"]),
                    last_price=float(row.get("last_price", 0.0)),
                    volume=int(row.get("volume", 0)),
                    open_interest=int(row.get("open_interest", 0)),
                )
            )
        return results
