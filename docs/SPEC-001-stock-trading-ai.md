# SPEC-001 — Stock Trading AI for SPY Options with LightGBM

## Background

This specification defines an MVP architecture for a stock trading AI system that uses a LightGBM multiclass model to generate SPY options paper-trading signals from historical and near-real-time market data.

The MVP is intentionally narrow:

- **SPY only** as the underlying.
- **Paper trading only** (no live execution).
- **Long call / long put / hold** signal outcomes.
- **Strict risk controls and audit logging**.

## Requirements

### Must Have

- Paper trading first, before live brokerage execution.
- SPY-focused ingest for OHLCV candles and options chain data.
- LightGBM-based signal generation.
- Prediction-to-intent mapping: `buy_call`, `buy_put`, or `hold`.
- Risk checks before every simulated order:
  - Max capital per trade
  - Max daily loss
  - Max open positions
  - Max option premium per contract
  - Min liquidity
  - Max bid/ask spread threshold
- Full audit trail: predictions, selected contracts, risk outcomes, paper orders, fills, exits, and equity.
- Dashboard/reporting for paper-trading performance.

### Should Have

- Historical backtesting and walk-forward validation.
- Key metrics (win rate, drawdown, Sharpe, profit factor, expectancy).
- Config-driven strategy and risk parameters.
- Scheduled retraining.
- Manual approval workflow before trade placement.

### Won’t Have in MVP

- Live money trading.
- Multi-broker production execution.
- Complex multi-leg options strategies.

## Architecture Overview

### Components

1. **Data Ingestion Service**
2. **Feature Engineering Service**
3. **Model Training Service (LightGBM)**
4. **Signal Service**
5. **Options Contract Selector**
6. **Risk Manager**
7. **Paper Trading Engine**
8. **Journal / Metrics Service**
9. **Dashboard**

### High-level flow

`Data -> Features -> Model -> Signal -> Selector -> Risk -> Paper Engine -> Journal -> Dashboard`

## Prediction Design

The model predicts SPY directional class over a configurable horizon:

- **Bullish**
- **Bearish**
- **Neutral**

Example labeling:

```text
future_return = (close[t + horizon] - close[t]) / close[t]

if future_return >= bullish_threshold:
    label = "bullish"
elif future_return <= bearish_threshold:
    label = "bearish"
else:
    label = "neutral"
```

Suggested defaults:

- Timeframe: 15m candles
- Horizon: 4 candles (~1 hour)
- Bullish threshold: +0.20%
- Bearish threshold: -0.20%
- DTE range for options: 7–30 calendar days

## Feature Set (MVP)

### Price/Volume

- Lagged returns (1,2,4,8,16)
- Rolling volatility (8,16,32,64)
- Volume ratio vs rolling mean
- High-low range, close-location value
- Gap from prior close
- Distance from VWAP

### Technical Indicators

- RSI
- MACD / histogram
- ATR
- Bollinger position / width
- Moving average slopes
- Realized volatility

### Options Features

- ATM IV
- Put/call volume and OI ratios (if available)
- ATM straddle proxy
- Spread percentage

### Calendar/Session

- Minute-of-day
- Day-of-week
- Days-to-expiration

## Signal Rules (example)

```text
if P(bullish) >= 0.60 and P(bullish) - P(neutral) >= 0.10:
    intent = "buy_call"
elif P(bearish) >= 0.60 and P(bearish) - P(neutral) >= 0.10:
    intent = "buy_put"
else:
    intent = "hold"
```

## Contract Selection Rules (MVP)

- Underlying: SPY
- DTE: 7–30
- Type: calls for bullish / puts for bearish
- Delta target: 0.35–0.60 absolute (if Greeks available)
- Min volume: 500
- Min open interest: 1,000
- Max spread: 10% of midpoint
- Max premium per contract: configurable

Rank by:
1) Delta proximity
2) Tight spread
3) Liquidity (volume/OI)
4) Lowest premium within risk

## Risk Management (initial defaults)

- Max account risk per trade: 1%
- Max premium per trade: 5%
- Max daily loss: 3%
- Max open positions: 3
- Max trades/day: 5
- Stop loss: 30–40% premium loss
- Take profit: 50–100% premium gain
- Time exit before expiration week / max hold window
- No-trade period: first 5 and last 10 market minutes

## Data Model (core tables)

- `market_candles`
- `options_chain_snapshots`
- `feature_rows`
- `model_versions`
- `predictions`
- `paper_trades`

Each table should include explicit timestamps and metadata columns sufficient for auditability.

## Implementation Plan

### Milestone 1 — Foundation

- Monorepo structure: `backend`, `dashboard`, `infra`, `docs`
- Docker Compose for backend, dashboard, postgres, redis, workers
- FastAPI skeleton + `/health`
- Next.js dashboard skeleton
- DB migration setup

### Milestone 2 — Ingestion

- SPY candle ingestion
- SPY options chain snapshots
- Normalization and dedup constraints

### Milestone 3 — Features + Labeling

- Indicator/feature builders
- Label generator
- No-lookahead tests

### Milestone 4 — Training

- Chronological split
- LightGBM multiclass training
- Walk-forward validation
- Artifact + metadata registry
- Manual approval step

### Milestone 5 — Signals + Contract Selection

- Inference service
- Probability-to-intent mapping
- Contract filtering/ranking with rejection reasons

### Milestone 6 — Paper Trading Engine

- Simulated account
- Order/fill simulation
- Exit rules
- P&L and journal records

### Milestone 7 — Dashboard

- Overview, signals, trades, models, backtests, settings pages

### Milestone 8 — Backtesting + Evaluation

- Historical replay
- Baseline strategy comparisons
- Report generation

### Milestone 9 — Paper Trading Pilot

- 20+ trading days monitoring
- Daily/weekly review workflow

## Minimum Test Coverage

- Feature engineering: no lookahead, deterministic outputs
- Labeling correctness
- Model training reproducibility and artifact registration
- Signal mapping correctness
- Contract filtering/ranking correctness
- Risk rejection behavior
- Paper engine fill/exit/P&L behavior
- API endpoint validation and pagination
- Dashboard rendering and API state handling

## Go/No-Go (paper pilot)

Suggested thresholds before expansion:

- 20+ trading days, 0 critical failures
- 100% auditable predictions + trades
- Drawdown below configured risk cap
- Profit factor > 1.1
- Positive expectancy after costs/slippage assumptions

## Security Controls

- Secrets only in env/secrets manager
- Backend-only key access
- Auth + role-based control before external exposure
- Full logging for configuration and trade lifecycle
- Live trading routes disabled in MVP

## Current Repository Next Step

Start with **Milestone 1 (Foundation)** by introducing the target directory layout and service skeletons in small, testable PRs.
