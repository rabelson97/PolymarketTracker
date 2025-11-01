"""Wallet analyzer for identifying qualifying wallets."""

from typing import List, Dict, Set
from datetime import datetime
from .models import Wallet, Bet
from .fetcher import PolymarketFetcher
from .config import MIN_WALLET_BALANCE, MIN_BET_MARGIN


class WalletAnalyzer:
    """Analyzes wallets to identify qualifying fresh wallets."""
    
    def __init__(self, fetcher: PolymarketFetcher):
        """Initialize the analyzer.
        
        Args:
            fetcher: PolymarketFetcher instance
        """
        self.fetcher = fetcher
    
    def find_qualifying_wallets(self) -> List[Wallet]:
        """Find wallets that meet all criteria.
        
        Returns:
            List of qualifying Wallet objects
        """
        print("Fetching recent trades...")
        trades = self.fetcher.fetch_recent_trades()
        
        if not trades:
            print("No trades found")
            return []
        
        print(f"Found {len(trades)} trades")
        
        # Group trades by wallet to find first bets
        wallet_trades: Dict[str, List[Dict]] = {}
        for trade in trades:
            addr = trade['wallet_address']
            if addr:
                if addr not in wallet_trades:
                    wallet_trades[addr] = []
                wallet_trades[addr].append(trade)
        
        qualifying_wallets = []
        checked_count = 0
        
        print(f"Analyzing {len(wallet_trades)} unique wallets...")
        
        for address, trades_list in wallet_trades.items():
            # Sort by timestamp to find first bet
            trades_list.sort(key=lambda x: x['timestamp'])
            first_trade = trades_list[0]
            
            # Calculate margin for first bet
            margin = self.fetcher.calculate_margin(
                first_trade['amount'], 
                first_trade['price']
            )
            
            # Debug: Show first few wallets
            if checked_count < 3:
                print(f"\nWallet {address[:10]}...")
                print(f"  First trade amount: {first_trade['amount']:.2f}")
                print(f"  Calculated margin: ${margin:.2f}")
            
            # Check if margin meets threshold
            if margin < MIN_BET_MARGIN:
                checked_count += 1
                continue
            
            # Check wallet balance
            if checked_count < 3:
                print(f"  ✓ Margin qualifies, checking balance...")
            
            balance = self.fetcher.get_wallet_balance(address)
            
            if checked_count < 3:
                print(f"  Balance: ${balance:.2f}")
            
            checked_count += 1
            
            if balance >= MIN_WALLET_BALANCE:
                wallet = Wallet(
                    address=address,
                    balance=balance,
                    first_bet_timestamp=first_trade['timestamp']
                )
                qualifying_wallets.append(wallet)
                print(f"✓ Qualifying wallet found: {address[:10]}... (${balance:,.2f})")
        
        return qualifying_wallets
