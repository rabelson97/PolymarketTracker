# How to Copy Smart Money Bets

## Quick Start

1. **Run the tracker:**
```bash
python -m src.polymarket_tracker.main
```

2. **You'll see output like this:**
```
⚡ MEDIUM SIGNALS (1):

1. 0x68dd6269... | $48,871 | 28.5% conviction
   Bet: $13,922
   👤 VIEW THEIR POLYMARKET PROFILE: https://polymarket.com/profile/0x68dd6269...
      (See all their active positions and betting history)
   ⚠️  Cluster: cluster_1 (coordinated activity)
```

3. **Click the Polymarket profile link** - You'll see ALL their bets!

## Step-by-Step: Finding What They Bet On

### Method 1: Polymarket Profile (EASIEST!)

1. Click the profile link from the output
2. You'll see their complete betting history:
   - All active positions
   - Position sizes
   - Which markets they're in
   - Their profit/loss

3. Look for recent bets (check timestamps match the signal)

4. **That's it!** You can see exactly what they bet on.

### Example

**Signal:**
```
1. 0x68dd6269... | $48,871 | 28.5% conviction
   Bet: $13,922
   👤 https://polymarket.com/profile/0x68dd6269bb89d27a850dcde0d59ee824a227f0b2
```

**What you'll see on their profile:**
- Active positions in specific markets
- How much they have in each position
- When they placed the bets
- Their total profit/loss

**Action:**
- Find the position that matches the $13,922 bet amount
- Click that market
- Consider placing a similar bet

## Understanding What You See

### High Conviction = Strong Signal

```
Conviction: 63.5%  ← They bet 63.5% of their balance!
```

**What this means:**
- 10-25% = Moderate confidence
- 25-50% = High confidence  
- 50%+ = VERY high confidence (rare!)
- 100%+ = All-in (extremely rare!)

### Cluster = Coordinated Activity

```
⚠️  Cluster: cluster_4 (coordinated activity)
```

**What this means:**
- 3+ wallets bet on the same market within 7 days
- Possible insider coordination
- Higher signal quality

## Example Walkthrough

**Signal Found:**
```
1. 0xfdd92e53... | $1,228 | 63.5% conviction
   Bet: $780
   📊 https://polygonscan.com/tx/0xe433259b...
   ⚠️  Cluster: cluster_12
```

**Analysis:**
1. **Conviction**: 63.5% - They're betting MORE THAN HALF their balance!
2. **Cluster**: Part of cluster_12 - Not acting alone
3. **Action**: This is a STRONG signal

**Steps to Copy:**
1. Click the PolygonScan link
2. Check the Logs tab to see which market/outcome
3. Go to Polymarket.com and find that market
4. Consider placing a similar bet (size according to your risk tolerance)

## Risk Management

**DON'T blindly copy 1:1!**

Instead:
- If they bet 50% of balance → You might bet 5-10%
- If they bet 10% of balance → You might bet 1-2%
- Always size according to YOUR risk tolerance

**Why?**
- They might have insider info you don't
- They might be wrong
- They might be hedging other positions
- You don't know their full strategy

## What to Look For

### 🔥 HIGHEST PRIORITY
- Conviction >50%
- Part of a cluster
- Recent (last 24 hours)
- STRONG signal quality

### ⚡ MEDIUM PRIORITY
- Conviction 10-50%
- MEDIUM signal quality
- May or may not be in cluster

### 📊 LOW PRIORITY
- Conviction <10%
- WEAK signal quality
- Likely just noise

## Troubleshooting

### "I can't find the market on Polymarket"

The market might be:
- Closed/resolved already
- Archived
- Very new (not indexed yet)

**Solution**: Check the transaction timestamp. If it's old (>7 days), the market may have resolved.

### "The transaction shows multiple tokens"

They might be:
- Buying multiple outcomes (hedging)
- Rebalancing a position
- Arbitraging

**Solution**: Look for the largest `amount` value - that's their main bet.

### "I found the market but odds have changed"

This is normal! The odds change as more people bet.

**Decision**:
- If odds moved in their favor → They got a better price
- If odds moved against them → Market disagrees with them
- Consider if the new odds still make sense

## Advanced: Tracking Performance

Keep a spreadsheet:
```
Date | Wallet | Conviction | Market | Your Bet | Outcome | Profit/Loss
```

After 10-20 bets, you'll see:
- Which conviction levels work best
- Which clusters are most accurate
- Your own win rate

## Quick Reference

**Files to check:**
- `output/smart_money_signals.json` - Full data
- `output/smart_money_signals.csv` - Spreadsheet format

**Key metrics:**
- Conviction ratio = Bet size / Balance
- Insider score = 0.0 to 1.0 (higher = more likely insider)
- Signal quality = STRONG > MEDIUM > WEAK

**When to act:**
- STRONG signals + High conviction + Cluster = Investigate immediately
- MEDIUM signals + >25% conviction = Worth following
- WEAK signals = Probably noise, skip

---

**Remember**: This is a tool to find informed traders, not a guarantee of success. Always do your own research and manage your risk appropriately.
