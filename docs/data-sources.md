# Data Source Plan (Milestone 2)

## Candle Data

- **Primary (free):** `yfinance` SPY historical candles for training/bootstrap.
- **Validation (optional):** Alpaca market data for cross-checking data quality and feed differences.

## Options Chain Data

For forward collection and delayed chain ingestion normalization:

- yfinance option chains
- Alpaca options market data (when available in account tier)
- Tradier delayed options chain payloads

## Current implementation status

- Candle ingestion supports `provider=yfinance`, `provider=alpaca`, and `provider=csv`.
- Options snapshot normalization supports provider mapping for `yfinance`, `alpaca`, `tradier`, and `internal` payloads.
