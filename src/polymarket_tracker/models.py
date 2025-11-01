"""Data models for Polymarket Tracker."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class BetDetails:
    """Details about a specific bet."""
    amount: float
    market_name: Optional[str]
    market_slug: Optional[str]
    market_category: Optional[str]
    insider_risk: str  # HIGH, MEDIUM, LOW
    outcome: Optional[str]
    timestamp: datetime
    tx_hash: str


@dataclass
class Wallet:
    """Represents a Polymarket wallet with signal scoring."""
    address: str
    balance: float
    first_bet: BetDetails
    conviction_ratio: float
    insider_score: float
    cluster_id: Optional[str]
    signal_quality: str  # STRONG, MEDIUM, WEAK


@dataclass
class Bet:
    """Represents a bet on Polymarket."""
    wallet_address: str
    market_id: str
    amount: float
    margin: float
    timestamp: datetime
