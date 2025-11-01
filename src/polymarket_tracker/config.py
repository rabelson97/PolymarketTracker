"""Configuration constants for Polymarket Tracker."""

# Original thresholds (now secondary signals)
MIN_WALLET_BALANCE = 50000  # USD
MIN_BET_MARGIN = 5000       # USD

# New conviction-based thresholds
MIN_CONVICTION_RATIO = 0.10  # 10% of portfolio
MIN_BALANCE_FOR_CONVICTION = 1000  # Minimum balance to calculate meaningful ratio

# Insider detection
MIN_CLUSTER_SIZE = 3  # Minimum wallets to identify as cluster
CLUSTER_WINDOW_DAYS = 7  # Days to look for coordinated activity

# Historical tracking
LOOKBACK_PERIOD = 7  # Days for recent activity
HISTORICAL_WINDOW = 90  # Days for win rate calculation

# High insider-risk market keywords
INSIDER_RISK_KEYWORDS = [
    'airdrop', 'token launch', 'tge', 'mainnet',
    'government', 'appointment', 'cabinet', 'secretary',
    'award', 'nobel', 'oscar', 'grammy',
    'merger', 'acquisition', 'm&a', 'ipo',
    'announcement', 'release date', 'launch date'
]
