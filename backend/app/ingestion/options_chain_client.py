"""Options-chain snapshot normalization utilities."""

from __future__ import annotations

import importlib
from datetime import datetime, timezone

from app.db.models import OptionsChainSnapshot


class OptionsChainClient:
    """Converts provider payloads into normalized options snapshots."""

    def normalize_snapshot(
        self,
        payload: list[dict],
        provider: str = "internal",
        snapshot_time: datetime | None = None,
    ) -> list[OptionsChainSnapshot]:
        when = snapshot_time or datetime.now(timezone.utc)
        provider_name = provider.lower()
        results: list[OptionsChainSnapshot] = []

        for row in payload:
            normalized = self._normalize_row(row=row, provider=provider_name)
            results.append(
                OptionsChainSnapshot(
                    underlying=normalized["underlying"],
                    option_symbol=normalized["option_symbol"],
                    snapshot_time=when,
                    expiration_date=normalized["expiration_date"],
                    strike=float(normalized["strike"]),
                    option_type=normalized["option_type"],
                    bid=float(normalized["bid"]),
                    ask=float(normalized["ask"]),
                    last_price=float(normalized.get("last_price", 0.0)),
                    volume=int(normalized.get("volume", 0)),
                    open_interest=int(normalized.get("open_interest", 0)),
                )
            )
        return results

    def fetch_yfinance_chain(self, symbol: str, expiration: str) -> list[dict]:
        yf = importlib.import_module("yfinance")
        ticker = yf.Ticker(symbol)
        chain = ticker.option_chain(expiration)

        calls = chain.calls.to_dict("records")
        puts = chain.puts.to_dict("records")
        payload: list[dict] = []

        for item in calls + puts:
            payload.append(
                {
                    "underlying": symbol,
                    "option_symbol": item["contractSymbol"],
                    "expiration_date": expiration,
                    "strike": item["strike"],
                    "option_type": "call" if "C" in item["contractSymbol"] else "put",
                    "bid": item.get("bid", 0.0),
                    "ask": item.get("ask", 0.0),
                    "last_price": item.get("lastPrice", 0.0),
                    "volume": item.get("volume", 0),
                    "open_interest": item.get("openInterest", 0),
                }
            )
        return payload

    def _normalize_row(self, row: dict, provider: str) -> dict:
        if provider in {"internal", "alpaca", "tradier"}:
            return row

        if provider == "yfinance":
            symbol = row.get("contractSymbol", "")
            return {
                "underlying": row.get("underlying", "SPY"),
                "option_symbol": symbol,
                "expiration_date": row["expiration_date"],
                "strike": row["strike"],
                "option_type": "call" if "C" in symbol else "put",
                "bid": row.get("bid", 0.0),
                "ask": row.get("ask", 0.0),
                "last_price": row.get("lastPrice", row.get("last_price", 0.0)),
                "volume": row.get("volume", 0),
                "open_interest": row.get("openInterest", row.get("open_interest", 0)),
            }

        raise ValueError(f"Unsupported provider: {provider}")
