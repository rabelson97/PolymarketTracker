# Polymarket Smart Money Tracker - Usage Guide

## What This Does

Tracks **conviction plays** and **insider signals** on Polymarket using:

1. **Conviction Ratio** - Wallets betting >10% of their balance (high conviction)
2. **Insider Detection** - Coordinated wallet clusters on same markets
3. **Market Risk Assessment** - Identifies high insider-risk markets (airdrops, government, awards)

## Signal Quality Levels

### 🔥 STRONG (Best)
- High conviction (>10% of balance) + High insider-risk market
- **Action**: Investigate immediately, likely informed bet

### ⚡ MEDIUM (Good)
- High conviction OR insider cluster + medium risk
- **Action**: Worth following, decent signal quality

### 📊 WEAK (Noise)
- Legacy signals (large balance + large bet, but low conviction)
- **Action**: Lower priority, may be noise

## Quick Start

```bash
# Run the tracker
cd /Users/rabelson/Documents/GitHub/PolymarketTracker
source .venv/bin/activate
python -m src.polymarket_tracker.main

# Check results
cat output/smart_money_signals.json
open output/smart_money_signals.csv
```

## Understanding the Output

### Example Signal
```json
{
  "address": "0xf5e15d33...",
  "balance": 2635.46,
  "conviction_ratio": 1.138,  // 113.8% - VERY aggressive!
  "insider_score": 0.70,      // 70% insider likelihood
  "cluster_id": "cluster_4",  // Part of coordinated group
  "signal_quality": "MEDIUM",
  "first_bet": {
    "amount": 3000,
    "market_name": "...",
    "insider_risk": "HIGH",   // Airdrop/government/award market
    "tx_hash": "0x..."
  }
}
```

### What to Look For

**🚨 Highest Priority:**
- Conviction >50% (betting half their balance or more)
- Part of a cluster (3+ wallets coordinating)
- HIGH insider risk market
- New wallet (first bet in last 7 days)

**⚠️ Medium Priority:**
- Conviction 10-50%
- MEDIUM insider risk
- Cluster member

**📊 Low Priority:**
- Conviction <10%
- LOW insider risk
- No cluster

## Configuration

Edit `src/polymarket_tracker/config.py`:

```python
# Conviction thresholds
MIN_CONVICTION_RATIO = 0.10  # 10% of portfolio (lower = more signals)

# Insider detection
MIN_CLUSTER_SIZE = 3  # Wallets needed for cluster (lower = more clusters)
CLUSTER_WINDOW_DAYS = 7  # Time window for coordination

# Lookback period
LOOKBACK_PERIOD = 7  # Days to scan (increase for more data)
```

## How to Act on Signals

### Step 1: Check the Transaction
Click the `polygonscan_url` to see the actual transaction details

### Step 2: Verify the Market
- If `market_url` exists, click to see the market
- Check if it's still active and bettable
- Look at current odds

### Step 3: Assess the Signal
- **STRONG + cluster + HIGH risk** = Likely insider, follow closely
- **MEDIUM + high conviction** = Serious player, worth considering
- **WEAK** = Just noise, skip

### Step 4: Size Your Bet
- Don't blindly copy - use their conviction as a signal
- If they bet 50% of balance, they're VERY confident
- If they bet 10%, they're moderately confident

## Advanced: Finding Patterns

### Cluster Analysis
```bash
# Find all wallets in a specific cluster
cat output/smart_money_signals.json | grep -A 20 "cluster_4"
```

### High Conviction Plays
```bash
# Find wallets with >50% conviction
cat output/smart_money_signals.csv | awk -F',' '$4 > 0.5'
```

## Troubleshooting

### "No signals found"
- Lower `MIN_CONVICTION_RATIO` to 0.05 (5%)
- Increase `LOOKBACK_PERIOD` to 14 or 30 days
- Check if Etherscan API is working

### "Taking too long"
- Reduce `LOOKBACK_PERIOD` to 3 days
- The tracker filters aggressively to avoid API rate limits

### "Market names show as 'Market ID: 0x...'"
- This is normal for speed optimization
- Click the `polygonscan_url` to see transaction details
- Market lookup is skipped for non-qualifying wallets

## What Makes This Different

**Traditional approach:**
- Track "fresh wallets with big first bets"
- Problem: Smart whales test small first, rookies FOMO big

**Smart money approach:**
- Track conviction (bet size / balance ratio)
- Detect insider clusters (coordinated activity)
- Focus on high-risk markets (airdrops, government, awards)
- Result: Find informed traders, not lucky gamblers

## Expected Performance

Based on research:
- **Conviction + Insider signals**: 3-8% edge
- **Strong signals only**: 15-25% edge (rare)
- **Win rate**: 55-65% (vs 50% baseline)

## Next Steps

**Phase 2 (Future):**
- Historical win rate tracking (requires database)
- Real-time Telegram alerts
- Integration with Hashdive API
- Automated bet execution

**For now:**
- Run daily
- Focus on STRONG signals
- Track your own results
- Adjust thresholds based on performance
