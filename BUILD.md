# Build Guide (Current Repo)

This repository now includes a full MVP architecture specification for a SPY options paper-trading system in:

- `docs/SPEC-001-stock-trading-ai.md`

## Milestone Status

- ✅ Milestone 1 (Foundation): started with backend service skeleton and `/health` endpoint.
- ✅ Milestone 2 (Market Data Ingestion): started with normalized candle/options ingestion clients, dedupe helpers, and ingestion tests.

## What you can run now

### 1) Install backend dependencies

```bash
pip install -r backend/requirements.txt
```

### 2) Run backend API

```bash
PYTHONPATH=backend uvicorn app.main:app --reload
```

### 3) Trigger candle ingestion

```bash
curl -X POST http://127.0.0.1:8000/jobs/ingest/candles
```

### 4) Run ingestion tests

```bash
PYTHONPATH=backend pytest backend/tests -q
```

## Next recommended tasks

1. Add persistence layer (PostgreSQL/TimescaleDB) for `market_candles` and `options_chain_snapshots`.
2. Add unique constraints matching dedupe keys.
3. Add provider adapters (Polygon/Alpaca) and retry/error handling.
4. Add ingestion scheduling and structured logs.
