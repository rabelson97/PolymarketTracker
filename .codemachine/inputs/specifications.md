# Specification: Polymarket Fresh Wallet Tracker

## Overview

A Python script that identifies "fresh wallets" on Polymarket that meet specific criteria: wallets with a balance of $50k or more that placed their first bet with a margin of $5k or more.

## Problem Statement

Tracking high-value new participants on Polymarket can provide insights into market activity and whale behavior. This tool automates the identification of fresh wallets (new participants) who enter the platform with significant capital and make substantial initial bets.

## Goals

- Identify wallets making their first bet on Polymarket
- Filter for wallets with balance ≥ $50,000
- Filter for first bets with margin ≥ $5,000
- Provide actionable data on these high-value fresh participants

## Non-Goals

- Real-time monitoring (batch processing is acceptable)
- Historical analysis beyond recent activity
- Wallet behavior prediction or analysis
- Integration with external notification systems

## User Stories

1. As a market analyst, I want to identify new high-value participants so I can understand market trends
2. As a trader, I want to track fresh whale wallets so I can observe their betting patterns
3. As a researcher, I want to export data on fresh wallets for further analysis

## Technical Design

### Architecture

```
┌─────────────────┐
│  Polymarket API │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Data Fetcher   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Wallet Analyzer │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Output/Report  │
└─────────────────┘
```

### Components

#### 1. API Client
- **Purpose**: Interface with Polymarket API
- **Endpoints needed**:
  - Get recent trades/bets
  - Get wallet information
  - Get wallet balance
  - Get wallet transaction history

#### 2. Wallet Analyzer
- **Purpose**: Process wallet data to identify fresh wallets
- **Logic**:
  - Check if wallet has only one bet (first bet)
  - Verify wallet balance ≥ $50,000
  - Verify bet margin ≥ $5,000
  - Calculate margin (difference between bet amount and potential payout)

#### 3. Data Storage
- **Purpose**: Cache results and avoid redundant API calls
- **Format**: JSON or SQLite for simplicity

#### 4. Reporter
- **Purpose**: Output results in usable format
- **Formats**: JSON, CSV, or console output

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
    outcome: str
    timestamp: datetime
    margin: float
```

### API Integration

**Polymarket API endpoints** (to be confirmed during implementation):
- `/trades` - Get recent trades
- `/markets` - Get market information
- Blockchain queries for wallet balances (USDC on Polygon)

### Algorithm

1. Fetch recent trades from Polymarket API
2. For each trade:
   - Extract wallet address
   - Check if wallet is "fresh" (first bet)
   - Query wallet balance
   - If balance ≥ $50k and bet margin ≥ $5k, record wallet
3. Output results

### Configuration

```python
MIN_WALLET_BALANCE = 50000  # USD
MIN_BET_MARGIN = 5000       # USD
LOOKBACK_PERIOD = 7         # days
```

## Implementation Plan

### Phase 1: API Integration
- Set up Polymarket API client
- Implement wallet balance queries
- Implement trade history queries

### Phase 2: Core Logic
- Implement fresh wallet detection
- Implement balance and margin filtering
- Add caching to avoid duplicate processing

### Phase 3: Output & Testing
- Implement output formatting
- Add error handling
- Test with real data

## Dependencies

- `requests` - HTTP client for API calls
- `web3` or `py-clob-client` - Polymarket/blockchain interaction
- `python-dotenv` - Configuration management
- `pandas` (optional) - Data manipulation

## Security & Privacy

- No private keys required (read-only operations)
- API rate limiting considerations
- Respect Polymarket's terms of service

## Testing Strategy

- Unit tests for wallet analysis logic
- Integration tests with Polymarket API (using test data)
- Validation of margin calculations

## Success Metrics

- Successfully identifies wallets meeting criteria
- Accurate balance and margin calculations
- Runs without errors for extended periods
- Processes data within reasonable time (< 5 minutes for 24h of data)

## Open Questions

1. What is the exact definition of "margin" in this context?
   - Potential loss vs potential gain?
   - Bet size relative to market odds?
2. How far back should we look for "fresh" wallets?
3. Should we track wallets over time or just identify them once?
4. Output format preference (JSON, CSV, database)?

## Future Enhancements

- Real-time monitoring with webhooks
- Notification system (email, Telegram, Discord)
- Historical trend analysis
- Wallet performance tracking over time
- Web dashboard for visualization
