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
        self.market_cache = {}  # Cache market details
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
            
            all_trades = []
            cutoff_time = datetime.now() - timedelta(days=LOOKBACK_PERIOD)
            
            # Fetch multiple pages to get more transactions
            for page in range(1, 6):  # 5 pages = 5000 transactions
                params = {
                    'chainid': '137',
                    'module': 'account',
                    'action': 'tokentx',
                    'contractaddress': USDC_CONTRACT,
                    'address': POLYMARKET_CTF_EXCHANGE,
                    'page': str(page),
                    'offset': '1000',
                    'sort': 'desc',
                    'apikey': self.api_key
                }
                
                print(f"  Fetching page {page}...")
                data = self._api_call(params)
                
                if data.get('status') != '1':
                    print(f"  API Error on page {page}: {data.get('message', 'Unknown error')}")
                    break
                
                transactions = data.get('result', [])
                if not transactions:
                    print(f"  No more transactions on page {page}")
                    break
                
                print(f"  Found {len(transactions)} transactions on page {page}")
                
                # Process transactions
                page_trades = 0
                for tx in transactions:
                    try:
                        timestamp = int(tx.get('timeStamp', 0))
                        tx_time = datetime.fromtimestamp(timestamp)
                        
                        # Stop if we've gone past the cutoff
                        if tx_time < cutoff_time:
                            print(f"  Reached cutoff date, stopping pagination")
                            break
                        
                        if tx.get('to', '').lower() == POLYMARKET_CTF_EXCHANGE.lower():
                            wallet_address = tx.get('from', '').lower()
                            value = float(tx.get('value', 0)) / 1e6
                            
                            if wallet_address and value > 0:
                                all_trades.append({
                                    'wallet_address': wallet_address,
                                    'market_id': tx.get('hash'),
                                    'amount': value,
                                    'price': 1.0,
                                    'timestamp': tx_time,
                                    'tx_hash': tx.get('hash')
                                })
                                page_trades += 1
                    except Exception:
                        continue
                
                print(f"  Collected {page_trades} deposits from page {page}")
                
                # If we hit the cutoff date, stop fetching more pages
                if tx_time < cutoff_time:
                    break
                
                # Rate limiting between pages
                time.sleep(0.3)
            
            print(f"\nTotal: Collected {len(all_trades)} USDC deposits from last {LOOKBACK_PERIOD} days")
            return all_trades
            
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
            
            time.sleep(0.1)  # Rate limiting (reduced for speed)
            data = self._api_call(params)
            
            if data.get('status') == '1':
                balance_raw = int(data.get('result', 0))
                balance_usd = balance_raw / 1e6
                return balance_usd
            
            return 0.0
        except Exception as e:
            return 0.0
    
    def get_market_details(self, token_id: str) -> dict:
        """Get market details - simplified for speed.
        
        Args:
            token_id: The token ID from the transaction
            
        Returns:
            Dictionary with market details including insider risk
        """
        # Check cache first
        if token_id in self.market_cache:
            return self.market_cache[token_id]
        
        # For speed, just return basic info without API lookup
        # Market name will be fetched only for qualifying wallets
        result = {
            'market_name': 'Unknown Market',
            'market_slug': '',
            'market_category': 'Unknown',
            'insider_risk': 'LOW',
            'outcome': 'Unknown'
        }
        
        self.market_cache[token_id] = result
        return result
    
    def get_market_details_full(self, token_id: str) -> dict:
        """Get full market details with API lookup (slower).
        
        Only call this for qualifying wallets.
        """
        # Check cache first
        if token_id in self.market_cache and self.market_cache[token_id]['market_name'] != 'Unknown Market':
            return self.market_cache[token_id]
        
        try:
            # Try active markets first
            search_url = f"https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=100"
            response = self.session.get(search_url, timeout=5)
            
            if response.status_code == 200:
                markets = response.json()
                for market in markets:
                    if market.get('id') == token_id or market.get('condition_id') == token_id:
                        market_name = market.get('question', 'Unknown Market')
                        category = market.get('category', 'Unknown')
                        insider_risk = self._assess_insider_risk(market_name, category)
                        
                        result = {
                            'market_name': market_name,
                            'market_slug': market.get('slug', ''),
                            'market_category': category,
                            'insider_risk': insider_risk,
                            'outcome': 'Unknown'
                        }
                        self.market_cache[token_id] = result
                        return result
        except Exception:
            pass
        
        result = {
            'market_name': f'Market ID: {token_id[:16]}...',
            'market_slug': '',
            'market_category': 'Unknown',
            'insider_risk': 'LOW',
            'outcome': 'Unknown'
        }
        self.market_cache[token_id] = result
        return result
    
    def _assess_insider_risk(self, market_name: str, category: str) -> str:
        """Assess insider risk level based on market name and category.
        
        Args:
            market_name: Market question text
            category: Market category
            
        Returns:
            Risk level: HIGH, MEDIUM, or LOW
        """
        from .config import INSIDER_RISK_KEYWORDS
        
        text = f"{market_name} {category}".lower()
        
        # Check for high-risk keywords
        keyword_matches = sum(1 for keyword in INSIDER_RISK_KEYWORDS if keyword in text)
        
        if keyword_matches >= 2:
            return 'HIGH'
        elif keyword_matches == 1:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def calculate_margin(self, amount: float, price: float) -> float:
        """Calculate bet margin.
        
        Args:
            amount: Bet amount
            price: Bet price (probability)
            
        Returns:
            Margin (potential loss)
        """
        return amount * price
