# PolymarketTracker

Track fresh wallets on Polymarket with balance ≥ $50k that placed their first bet with ≥ $5k margin.

## Overview

This project identifies new high-value participants on Polymarket who:
- Have a wallet balance of $50,000 or more
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

4. Configure settings (optional):
```bash
cp .env.example .env
# Edit .env to customize parameters
```

## Usage

Run the tracker:
```bash
python -m src.polymarket_tracker.main
```

The tracker will:
1. Fetch recent trades from Polymarket (last 7 days)
2. Identify wallets making their first bet
3. Filter for wallets with balance ≥ $50,000
4. Filter for first bet margin ≥ $5,000
5. Export results to `output/` directory

### Output

Results are exported in two formats:
- `output/qualifying_wallets.json` - JSON format
- `output/qualifying_wallets.csv` - CSV format

### Configuration

Edit `src/polymarket_tracker/config.py` to adjust:
- `MIN_WALLET_BALANCE` - Minimum wallet balance (default: $50,000)
- `MIN_BET_MARGIN` - Minimum first bet margin (default: $5,000)
- `LOOKBACK_PERIOD` - Days to look back (default: 7)

## License

See [LICENSE](LICENSE)
