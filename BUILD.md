# Build Guide (Current Repo)

This repository includes the MVP architecture spec in:

- `docs/SPEC-001-stock-trading-ai.md`

## Milestone Status

- ✅ Milestone 1 (Foundation): backend service skeleton and `/health` endpoint.
- ✅ Milestone 2 (Market Data Ingestion): provider-aware candle/options ingestion adapters and tests.

## Data Ingestion Sources (as requested)

- **Primary free training data:** `yfinance` SPY historical candles.
- **Optional free/cheap validation source:** Alpaca market data.
- **Options chain for forward collection:** yfinance, Alpaca, or Tradier delayed chain payload normalization.

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

**yfinance (default):**

```bash
curl -X POST "http://127.0.0.1:8000/jobs/ingest/candles?provider=yfinance&timeframe=1d&start=2025-01-01&end=2025-12-31"
```

**Alpaca validation source:**

```bash
ALPACA_API_KEY=... ALPACA_SECRET_KEY=... PYTHONPATH=backend uvicorn app.main:app --reload
curl -X POST "http://127.0.0.1:8000/jobs/ingest/candles?provider=alpaca&timeframe=1Day&start=2025-01-01&end=2025-12-31"
```

**Local CSV fallback:**

```bash
curl -X POST "http://127.0.0.1:8000/jobs/ingest/candles?provider=csv&csv_path=backend/fixtures/spy_candles_fixture.csv&timeframe=15m"
```

### 4) Run ingestion tests

```bash
PYTHONPATH=backend pytest backend/tests -q
```

## Next recommended tasks

1. Persist candles/options snapshots into PostgreSQL/TimescaleDB.
2. Add unique constraints matching current dedupe keys.
3. Add scheduled ingestion jobs with structured error/audit logs.
4. Add provider-specific adapters for live delayed options chain pulls.
