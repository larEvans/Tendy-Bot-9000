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
## What to run right now

Current repository contents are still minimal (single-script style). You can run:

```bash
python lstm.py
```

## Build from spec

Use `docs/SPEC-001-stock-trading-ai.md` as the implementation blueprint and execute work in milestone order, beginning with **Milestone 1: Foundation**.

Recommended first implementation tasks:

1. Create monorepo folders: `backend/`, `dashboard/`, `infra/`, `docs/`.
2. Add Docker Compose for local stack.
3. Add FastAPI `/health` endpoint.
4. Add dashboard skeleton.
5. Add DB migration tooling.
