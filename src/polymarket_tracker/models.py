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
    outcome: Optional[str]
    timestamp: datetime
    tx_hash: str


@dataclass
class Wallet:
    """Represents a Polymarket wallet."""
    address: str
    balance: float
    first_bet: BetDetails


@dataclass
class Bet:
    """Represents a bet on Polymarket."""
    wallet_address: str
    market_id: str
    amount: float
    margin: float
    timestamp: datetime
