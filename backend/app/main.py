from __future__ import annotations

from fastapi import FastAPI

from app.ingestion.jobs import ingest_spy_candles

app = FastAPI(title="SPY Options AI Backend", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/jobs/ingest/candles")
def run_candle_ingestion() -> dict[str, int | str]:
    candles, audit = ingest_spy_candles()
    return {
        "source": audit.source,
        "records_in": audit.records_in,
        "records_out": audit.records_out,
        "symbol": candles[0].symbol if candles else "SPY",
    }
