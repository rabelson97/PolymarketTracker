"""Polymarket API data fetcher."""

import os
import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dotenv import load_dotenv
from .models import Bet
from .config import LOOKBACK_PERIOD

load_dotenv()

# Polymarket CTF Exchange contract on Polygon
POLYMARKET_CTF_EXCHANGE = "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"
# USDC contract on Polygon
USDC_CONTRACT = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"


class PolymarketFetcher:
    """Fetches data from Polymarket via Etherscan API V2."""
    
    def __init__(self):
        """Initialize the Polymarket fetcher with Etherscan API V2."""
        self.api_key = os.getenv("ETHERSCAN_API_KEY")
        
        if not self.api_key:
            raise ValueError("Missing ETHERSCAN_API_KEY environment variable")
        
        self.base_url = "https://api.etherscan.io/v2/api"
        self.session = requests.Session()
        print("Initialized with Etherscan API V2 (Polygon)")
    
    def _api_call(self, params: dict, retries: int = 2) -> dict:
        """Make API call with retry logic."""
        for attempt in range(retries):
            try:
                response = self.session.get(self.base_url, params=params, timeout=45)
                return response.json()
            except requests.exceptions.Timeout:
                if attempt < retries - 1:
                    print(f"Timeout, retrying...")
                    time.sleep(3)
                else:
                    raise
        return {}
    
    def fetch_recent_trades(self) -> List[Dict[str, Any]]:
        """Fetch recent trades from Polymarket via blockchain data.
        
        Returns:
            List of trade dictionaries
        """
        try:
            print("Fetching recent USDC transfers to Polymarket...")
            
            params = {
                'chainid': '137',
                'module': 'account',
                'action': 'tokentx',
                'contractaddress': USDC_CONTRACT,
                'address': POLYMARKET_CTF_EXCHANGE,
                'page': '1',
                'offset': '1000',  # Reduced from 2000
                'sort': 'desc',
                'apikey': self.api_key
            }
            
            data = self._api_call(params)
            
            if data.get('status') != '1':
                print(f"API Error: {data.get('message', 'Unknown error')}")
                return []
            
            transactions = data.get('result', [])
            print(f"Found {len(transactions)} recent USDC transfers")
            
            trades = []
            cutoff_time = datetime.now() - timedelta(days=LOOKBACK_PERIOD)
            
            for tx in transactions:
                try:
                    timestamp = int(tx.get('timeStamp', 0))
                    tx_time = datetime.fromtimestamp(timestamp)
                    
                    if tx_time < cutoff_time:
                        continue
                    
                    if tx.get('to', '').lower() == POLYMARKET_CTF_EXCHANGE.lower():
                        wallet_address = tx.get('from', '').lower()
                        value = float(tx.get('value', 0)) / 1e6
                        
                        if wallet_address and value > 0:
                            trades.append({
                                'wallet_address': wallet_address,
                                'market_id': tx.get('hash'),
                                'amount': value,
                                'price': 1.0,
                                'timestamp': tx_time,
                                'tx_hash': tx.get('hash')
                            })
                except Exception:
                    continue
            
            print(f"Collected {len(trades)} USDC deposits from last {LOOKBACK_PERIOD} days")
            return trades
            
        except Exception as e:
            print(f"Error fetching trades: {e}")
            return []
    
    def get_wallet_balance(self, address: str) -> float:
        """Get wallet USDC balance from Etherscan API.
        
        Args:
            address: Wallet address
            
        Returns:
            Wallet USDC balance in USD
        """
        try:
            params = {
                'chainid': '137',
                'module': 'account',
                'action': 'tokenbalance',
                'contractaddress': USDC_CONTRACT,
                'address': address,
                'tag': 'latest',
                'apikey': self.api_key
            }
            
            time.sleep(0.2)  # Rate limiting
            data = self._api_call(params)
            
            if data.get('status') == '1':
                balance_raw = int(data.get('result', 0))
                balance_usd = balance_raw / 1e6
                return balance_usd
            
            return 0.0
        except Exception as e:
            return 0.0
    
    def get_market_details(self, token_id: str) -> dict:
        """Get market details from Polymarket Gamma API.
        
        Args:
            token_id: The token ID from the transaction
            
        Returns:
            Dictionary with market details
        """
        try:
            # Query Polymarket's Gamma API for market info
            url = f"https://gamma-api.polymarket.com/markets/{token_id}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'market_name': data.get('question', 'Unknown Market'),
                    'market_slug': data.get('slug', ''),
                    'outcome': data.get('outcome', 'Unknown')
                }
            
            # Try searching by condition ID
            search_url = f"https://gamma-api.polymarket.com/markets?condition_id={token_id}"
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    market = data[0]
                    return {
                        'market_name': market.get('question', 'Unknown Market'),
                        'market_slug': market.get('slug', ''),
                        'outcome': 'Unknown'
                    }
            
            return {
                'market_name': 'Unknown Market',
                'market_slug': '',
                'outcome': 'Unknown'
            }
        except Exception as e:
            return {
                'market_name': 'Unknown Market',
                'market_slug': '',
                'outcome': 'Unknown'
            }
    
    def calculate_margin(self, amount: float, price: float) -> float:
        """Calculate bet margin.
        
        Args:
            amount: Bet amount
            price: Bet price (probability)
            
        Returns:
            Margin (potential loss)
        """
        return amount * price
