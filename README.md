# PolymarketTracker

Track fresh wallets on Polymarket with balance ≥ $50k that placed their first bet with ≥ $5k margin.

## Overview

This project identifies new high-value participants on Polymarket who:
- Have a wallet balance of $50,000 or more (USDC)
- Placed their first bet with a margin of $5,000 or more

## Specification

See [`spec/SPEC.md`](spec/SPEC.md) for the complete specification.

## Development

This project follows **Spec-Driven Development (SDD)** using [GitHub Spec Kit](https://github.com/github/spec-kit).

### Getting Started

1. Read the specification: `spec/SPEC.md`
2. Use Amazon Q Developer: `/implement-spec`
3. Follow the spec exactly

### Project Structure

```
spec/
  SPEC.md              # Main specification
.amazonq/prompts/      # Amazon Q Developer prompts
memory/                # Project memory and context
templates/             # Spec-kit templates
scripts/               # Utility scripts
src/
  polymarket_tracker/  # Main application code
output/                # Generated reports (gitignored)
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd PolymarketTracker
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up Etherscan API key:
```bash
# Add to your ~/.zshrc or ~/.bashrc
export ETHERSCAN_API_KEY='your_api_key_here'

# Reload your shell
source ~/.zshrc  # or source ~/.bashrc
```

**Get a free Etherscan API key:** https://etherscan.io/apis

## Usage

Run the tracker:
```bash
python -m src.polymarket_tracker.main
```

### Example Output

```
============================================================
Polymarket Fresh Wallet Tracker
============================================================
Started at: 2025-11-01 14:24:35

Initialized with Etherscan API V2 (Polygon)
Fetching recent trades...
Fetching recent USDC transfers to Polymarket...
Found 1000 recent USDC transfers
Collected 581 USDC deposits from last 7 days
Found 581 trades
Analyzing 238 unique wallets...

✓ Qualifying wallet found: 0x31519628... ($500,351.44)
✓ Qualifying wallet found: 0xdbade4c8... ($173,960.23)

============================================================
Found 2 qualifying wallets
============================================================

Qualifying Wallets:

1. Address: 0x31519628fb5e5aa559d4ba27aa1248810b9f0977
   Balance: $500,351.44
   First Bet: 2025-11-01 14:23:06

2. Address: 0xdbade4c82fb72780a0db9a38f821d8671aba9c95
   Balance: $173,960.23
   First Bet: 2025-11-01 14:23:18

✓ Exported to output/qualifying_wallets.json
✓ Exported to output/qualifying_wallets.csv

Completed at: 2025-11-01 14:24:49
```

### Output Files

Results are exported to the `output/` directory:

- **`output/qualifying_wallets.json`** - JSON format with wallet details
- **`output/qualifying_wallets.csv`** - CSV format for spreadsheet analysis

Example JSON output:
```json
[
  {
    "address": "0x31519628fb5e5aa559d4ba27aa1248810b9f0977",
    "balance": 500351.44,
    "first_bet_timestamp": "2025-11-01T14:23:06"
  }
]
```

Example CSV output:
```csv
Address,Balance (USD),First Bet Timestamp
0x31519628fb5e5aa559d4ba27aa1248810b9f0977,500351.44,2025-11-01T14:23:06
```

## Configuration

Edit `src/polymarket_tracker/config.py` to adjust tracking parameters:

```python
MIN_WALLET_BALANCE = 50000  # Minimum wallet balance in USD
MIN_BET_MARGIN = 5000       # Minimum first bet margin in USD
LOOKBACK_PERIOD = 7         # Days to look back for trades
```

## How It Works

1. **Fetches blockchain data** - Queries Polygon blockchain via Etherscan API V2 for USDC transfers to Polymarket's CTF Exchange contract
2. **Identifies first bets** - Groups transactions by wallet address and finds the first bet for each wallet
3. **Filters by margin** - Checks if the first bet amount meets the minimum threshold ($5,000)
4. **Checks balance** - Queries current USDC balance for qualifying wallets
5. **Filters by balance** - Only includes wallets with balance ≥ $50,000
6. **Exports results** - Saves qualifying wallets to JSON and CSV files

## Technical Details

- **Blockchain**: Polygon (Chain ID: 137)
- **Contract**: Polymarket CTF Exchange (`0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E`)
- **Token**: USDC (`0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174`)
- **API**: Etherscan API V2 for Polygon blockchain data
- **Rate Limiting**: Built-in retry logic and delays to respect API limits

## Troubleshooting

### API Rate Limits

If you encounter timeout errors:
- The free Etherscan API tier has rate limits
- The tracker includes automatic retry logic
- Consider upgrading to a paid API plan for higher limits

### No Qualifying Wallets Found

This is normal if:
- No new wallets met the criteria in the lookback period
- Try increasing `LOOKBACK_PERIOD` in config.py
- Or lowering thresholds temporarily to test

### Missing API Key

Error: `Missing ETHERSCAN_API_KEY environment variable`

Solution:
```bash
export ETHERSCAN_API_KEY='your_key_here'
source ~/.zshrc
```

## License

See [LICENSE](LICENSE)
