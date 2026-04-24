"""Historical OHLCV ingestion from CSV and market-data providers."""

from __future__ import annotations

import csv
import importlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.db.models import MarketCandle


class MarketDataClient:
    """Loads normalized OHLCV candles from CSV, yfinance, or Alpaca."""

    def load_spy_candles(
        self,
        *,
        provider: str,
        symbol: str,
        timeframe: str,
        csv_path: str | None = None,
        start: str | None = None,
        end: str | None = None,
        alpaca_api_key: str | None = None,
        alpaca_secret_key: str | None = None,
        alpaca_data_base_url: str | None = None,
    ) -> list[MarketCandle]:
        provider_name = provider.lower()

        if provider_name == "csv":
            if not csv_path:
                raise ValueError("csv_path is required when provider=csv")
            return self.load_candles_from_csv(csv_path=csv_path, symbol=symbol, timeframe=timeframe)

        if provider_name == "yfinance":
            return self.load_candles_from_yfinance(symbol=symbol, timeframe=timeframe, start=start, end=end)

        if provider_name == "alpaca":
            return self.load_candles_from_alpaca(
                symbol=symbol,
                timeframe=timeframe,
                start=start,
                end=end,
                alpaca_api_key=alpaca_api_key or "",
                alpaca_secret_key=alpaca_secret_key or "",
                alpaca_data_base_url=alpaca_data_base_url or "https://data.alpaca.markets",
            )

        raise ValueError(f"Unsupported provider: {provider}")

    def load_candles_from_csv(self, csv_path: str, symbol: str, timeframe: str) -> list[MarketCandle]:
        rows = list(self._read_rows(csv_path))
        return [
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
            for row in rows
        ]

    def load_candles_from_yfinance(
        self,
        *,
        symbol: str,
        timeframe: str,
        start: str | None,
        end: str | None,
    ) -> list[MarketCandle]:
        yf = importlib.import_module("yfinance")
        ticker = yf.Ticker(symbol)
        history = ticker.history(interval=timeframe, start=start, end=end, auto_adjust=False)

        candles: list[MarketCandle] = []
        for ts, row in history.iterrows():
            timestamp = ts.to_pydatetime()
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            candles.append(
                MarketCandle(
                    symbol=symbol,
                    timeframe=timeframe,
                    timestamp=timestamp.astimezone(timezone.utc),
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    volume=int(float(row.get("Volume", 0))),
                )
            )
        return candles

    def load_candles_from_alpaca(
        self,
        *,
        symbol: str,
        timeframe: str,
        start: str | None,
        end: str | None,
        alpaca_api_key: str,
        alpaca_secret_key: str,
        alpaca_data_base_url: str,
    ) -> list[MarketCandle]:
        params = {
            "timeframe": timeframe,
            "start": start,
            "end": end,
            "limit": 10000,
            "adjustment": "raw",
            "feed": "iex",
        }
        query = urlencode({k: v for k, v in params.items() if v})
        url = f"{alpaca_data_base_url.rstrip('/')}/v2/stocks/{symbol}/bars?{query}"
        req = Request(
            url,
            headers={
                "accept": "application/json",
                "APCA-API-KEY-ID": alpaca_api_key,
                "APCA-API-SECRET-KEY": alpaca_secret_key,
            },
        )

        with urlopen(req, timeout=20) as resp:
            body = json.loads(resp.read().decode("utf-8"))

        bars = body.get("bars", [])
        candles: list[MarketCandle] = []
        for bar in bars:
            candles.append(
                MarketCandle(
                    symbol=symbol,
                    timeframe=timeframe,
                    timestamp=datetime.fromisoformat(bar["t"].replace("Z", "+00:00")).astimezone(timezone.utc),
                    open=float(bar["o"]),
                    high=float(bar["h"]),
                    low=float(bar["l"]),
                    close=float(bar["c"]),
                    volume=int(bar.get("v", 0)),
                )
            )
        return candles

    def _read_rows(self, csv_path: str) -> Iterable[dict[str, str]]:
        path = Path(csv_path)
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            yield from reader
