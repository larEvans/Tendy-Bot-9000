from __future__ import annotations

from fastapi import FastAPI, Query

from app.ingestion.jobs import ingest_spy_candles

app = FastAPI(title="SPY Options AI Backend", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/jobs/ingest/candles")
def run_candle_ingestion(
    provider: str = Query(default="yfinance", description="csv | yfinance | alpaca"),
    start: str | None = Query(default=None, description="ISO date for historical pull"),
    end: str | None = Query(default=None, description="ISO date for historical pull"),
    timeframe: str = Query(default="1d", description="bar timeframe, e.g. 1d, 1h, 15m"),
    csv_path: str | None = Query(default=None, description="used when provider=csv"),
) -> dict[str, int | str]:
    candles, audit = ingest_spy_candles(
        provider=provider,
        csv_path=csv_path,
        start=start,
        end=end,
        timeframe=timeframe,
    )
    return {
        "source": audit.source,
        "records_in": audit.records_in,
        "records_out": audit.records_out,
        "symbol": candles[0].symbol if candles else "SPY",
    }
