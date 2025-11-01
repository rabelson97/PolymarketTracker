# Specification: Polymarket Fresh Wallet Tracker

## Overview

Track fresh wallets on Polymarket with balance ≥ $50k that placed their first bet with ≥ $5k margin.

## Problem Statement

Identify new high-value participants entering Polymarket with significant capital and substantial initial bets.

## Requirements

### Functional Requirements

1. **Wallet Identification**
   - Detect wallets making their first bet on Polymarket
   - Verify wallet balance ≥ $50,000
   - Verify first bet margin ≥ $5,000

2. **Data Collection**
   - Query Polymarket API for recent trades
   - Retrieve wallet balance information
   - Calculate bet margins

3. **Output**
   - Display identified wallets with relevant metrics
   - Export data in structured format (JSON/CSV)

### Non-Functional Requirements

- Read-only operations (no wallet interactions)
- Respect API rate limits
- Process data efficiently (< 5 min for 24h data)

## Technical Design

### Architecture

```
Polymarket API → Data Fetcher → Wallet Analyzer → Output
```

### Data Models

```python
@dataclass
class Wallet:
    address: str
    balance: float
    first_bet_timestamp: datetime

@dataclass
class Bet:
    wallet_address: str
    market_id: str
    amount: float
    margin: float
    timestamp: datetime
```

### Algorithm

1. Fetch recent trades from Polymarket API
2. For each trade:
   - Extract wallet address
   - Check if first bet for wallet
   - Query wallet balance
   - If balance ≥ $50k AND margin ≥ $5k → record
3. Output results

### Configuration

```python
MIN_WALLET_BALANCE = 50000  # USD
MIN_BET_MARGIN = 5000       # USD
LOOKBACK_PERIOD = 7         # days
```

## Dependencies

- `py-clob-client` - Polymarket API client
- `requests` - HTTP client
- `python-dotenv` - Configuration
- `pandas` - Data manipulation (optional)

## Success Criteria

- Accurately identifies qualifying wallets
- Correct balance and margin calculations
- Handles API errors gracefully
- Completes processing within time limit

## Open Questions

1. Margin definition: potential loss vs gain, or bet size relative to odds?
2. Lookback period for "fresh" wallet determination?
3. Preferred output format?
