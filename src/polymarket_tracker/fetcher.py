"""Polymarket API data fetcher."""

from datetime import datetime, timedelta
from typing import List, Dict, Any
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
from .models import Bet
from .config import LOOKBACK_PERIOD


class PolymarketFetcher:
    """Fetches data from Polymarket API."""
    
    def __init__(self, host: str = "https://clob.polymarket.com"):
        """Initialize the Polymarket fetcher.
        
        Args:
            host: Polymarket CLOB API host URL
        """
        self.client = ClobClient(host, key="", chain_id=137)
    
    def fetch_recent_trades(self) -> List[Dict[str, Any]]:
        """Fetch recent trades from Polymarket.
        
        Returns:
            List of trade dictionaries
        """
        try:
            # Get markets to find recent trades
            markets = self.client.get_markets()
            
            trades = []
            cutoff_time = datetime.now() - timedelta(days=LOOKBACK_PERIOD)
            
            for market in markets[:50]:  # Limit to avoid rate limits
                try:
                    market_trades = self.client.get_trades(market['condition_id'])
                    for trade in market_trades:
                        trade_time = datetime.fromtimestamp(int(trade.get('timestamp', 0)))
                        if trade_time >= cutoff_time:
                            trades.append({
                                'wallet_address': trade.get('maker_address') or trade.get('taker_address'),
                                'market_id': market['condition_id'],
                                'amount': float(trade.get('size', 0)),
                                'price': float(trade.get('price', 0)),
                                'timestamp': trade_time
                            })
                except Exception as e:
                    print(f"Error fetching trades for market {market.get('condition_id')}: {e}")
                    continue
            
            return trades
        except Exception as e:
            print(f"Error fetching markets: {e}")
            return []
    
    def get_wallet_balance(self, address: str) -> float:
        """Get wallet balance from Polymarket.
        
        Args:
            address: Wallet address
            
        Returns:
            Wallet balance in USD
        """
        try:
            # Get wallet's open orders and positions
            orders = self.client.get_orders(address)
            total = sum(float(order.get('size', 0)) * float(order.get('price', 0)) 
                       for order in orders)
            return total
        except Exception as e:
            print(f"Error fetching balance for {address}: {e}")
            return 0.0
    
    def calculate_margin(self, amount: float, price: float) -> float:
        """Calculate bet margin.
        
        Args:
            amount: Bet amount
            price: Bet price (probability)
            
        Returns:
            Margin (potential loss)
        """
        # Margin = amount at risk = bet size * price
        return amount * price
