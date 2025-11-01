"""Data models for Polymarket Tracker."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Wallet:
    """Represents a Polymarket wallet."""
    address: str
    balance: float
    first_bet_timestamp: datetime


@dataclass
class Bet:
    """Represents a bet on Polymarket."""
    wallet_address: str
    market_id: str
    amount: float
    margin: float
    timestamp: datetime
