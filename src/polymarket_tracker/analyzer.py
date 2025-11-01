"""Wallet analyzer with conviction and insider detection."""

from typing import List, Dict, Set
from datetime import datetime, timedelta
from collections import defaultdict
from .models import Wallet, Bet, BetDetails
from .fetcher import PolymarketFetcher
from .config import (
    MIN_WALLET_BALANCE, MIN_BET_MARGIN, MIN_CONVICTION_RATIO,
    MIN_BALANCE_FOR_CONVICTION, MIN_CLUSTER_SIZE, CLUSTER_WINDOW_DAYS
)


class WalletAnalyzer:
    """Analyzes wallets for conviction plays and insider signals."""
    
    def __init__(self, fetcher: PolymarketFetcher):
        self.fetcher = fetcher
    
    def calculate_conviction_ratio(self, bet_amount: float, wallet_balance: float) -> float:
        """Calculate bet size as percentage of wallet balance."""
        if wallet_balance < MIN_BALANCE_FOR_CONVICTION:
            return 0.0
        return bet_amount / wallet_balance if wallet_balance > 0 else 0.0
    
    def calculate_insider_score(self, wallet_data: dict, cluster_id: str = None) -> float:
        """Calculate insider likelihood score (0.0 to 1.0).
        
        Factors:
        - New wallet (first bet recent)
        - High conviction (>10% of balance)
        - High insider-risk market
        - Part of coordinated cluster
        """
        score = 0.0
        
        # New wallet bonus (0.3)
        days_since_first = (datetime.now() - wallet_data['first_bet_time']).days
        if days_since_first <= 7:
            score += 0.3
        elif days_since_first <= 30:
            score += 0.15
        
        # High conviction bonus (0.3)
        if wallet_data['conviction_ratio'] >= 0.25:  # 25%+
            score += 0.3
        elif wallet_data['conviction_ratio'] >= 0.10:  # 10%+
            score += 0.15
        
        # Insider-risk market bonus (0.3)
        if wallet_data['insider_risk'] == 'HIGH':
            score += 0.3
        elif wallet_data['insider_risk'] == 'MEDIUM':
            score += 0.15
        
        # Cluster coordination bonus (0.1)
        if cluster_id:
            score += 0.1
        
        return min(score, 1.0)
    
    def detect_clusters(self, wallet_trades: Dict[str, List[Dict]]) -> Dict[str, str]:
        """Detect coordinated wallet clusters.
        
        Returns:
            Dict mapping wallet_address -> cluster_id
        """
        # Group by market and time window
        market_wallets = defaultdict(list)
        
        for address, trades in wallet_trades.items():
            first_trade = min(trades, key=lambda x: x['timestamp'])
            market_id = first_trade.get('market_id')
            
            market_wallets[market_id].append({
                'address': address,
                'timestamp': first_trade['timestamp'],
                'amount': first_trade['amount']
            })
        
        # Find clusters (3+ wallets on same market within window)
        clusters = {}
        cluster_counter = 0
        
        for market_id, wallets in market_wallets.items():
            if len(wallets) < MIN_CLUSTER_SIZE:
                continue
            
            # Sort by timestamp
            wallets.sort(key=lambda x: x['timestamp'])
            
            # Check if wallets are within time window
            for i in range(len(wallets) - MIN_CLUSTER_SIZE + 1):
                window_wallets = []
                base_time = wallets[i]['timestamp']
                
                for j in range(i, len(wallets)):
                    if (wallets[j]['timestamp'] - base_time).days <= CLUSTER_WINDOW_DAYS:
                        window_wallets.append(wallets[j])
                
                if len(window_wallets) >= MIN_CLUSTER_SIZE:
                    cluster_counter += 1
                    cluster_id = f"cluster_{cluster_counter}"
                    for w in window_wallets:
                        clusters[w['address']] = cluster_id
                    break
        
        return clusters
    
    def find_qualifying_wallets(self) -> List[Wallet]:
        """Find wallets with strong conviction or insider signals."""
        print("Fetching recent trades...")
        trades = self.fetcher.fetch_recent_trades()
        
        if not trades:
            print("No trades found")
            return []
        
        print(f"Found {len(trades)} trades")
        
        # Group trades by wallet
        wallet_trades: Dict[str, List[Dict]] = {}
        for trade in trades:
            addr = trade['wallet_address']
            if addr:
                if addr not in wallet_trades:
                    wallet_trades[addr] = []
                wallet_trades[addr].append(trade)
        
        print(f"Analyzing {len(wallet_trades)} unique wallets...")
        
        # Detect clusters
        print("Detecting coordinated wallet clusters...")
        clusters = self.detect_clusters(wallet_trades)
        if clusters:
            print(f"Found {len(set(clusters.values()))} potential insider clusters")
        
        qualifying_wallets = []
        conviction_qualified = 0
        insider_qualified = 0
        
        for address, trades_list in wallet_trades.items():
            # Get first bet
            trades_list.sort(key=lambda x: x['timestamp'])
            first_trade = trades_list[0]
            
            # Quick filter: Skip tiny bets
            if first_trade['amount'] < 50:  # Less than $50
                continue
            
            # Calculate conviction ratio (estimate with placeholder balance)
            # We'll get real balance only for promising wallets
            estimated_balance = first_trade['amount'] * 10  # Conservative estimate
            estimated_conviction = first_trade['amount'] / estimated_balance
            
            # Pre-filter: Only proceed if bet size is meaningful
            if first_trade['amount'] < 1000 and estimated_conviction < 0.05:
                continue
            
            # NOW get the actual balance (only for promising wallets)
            balance = self.fetcher.get_wallet_balance(address)
            
            # Calculate real conviction ratio
            conviction_ratio = self.calculate_conviction_ratio(first_trade['amount'], balance)
            
            # Quick pre-filter: Skip if no conviction and low balance
            if conviction_ratio < MIN_CONVICTION_RATIO and balance < MIN_WALLET_BALANCE:
                continue
            
            # Only fetch full market details if wallet might qualify
            market_details = self.fetcher.get_market_details_full(first_trade.get('market_id', ''))
            
            # Prepare wallet data for scoring
            wallet_data = {
                'first_bet_time': first_trade['timestamp'],
                'conviction_ratio': conviction_ratio,
                'insider_risk': market_details.get('insider_risk', 'LOW')
            }
            
            # Calculate insider score
            cluster_id = clusters.get(address)
            insider_score = self.calculate_insider_score(wallet_data, cluster_id)
            
            # Determine signal quality
            signal_quality = 'WEAK'
            qualifies = False
            
            # STRONG signal: High conviction + High insider risk
            if conviction_ratio >= MIN_CONVICTION_RATIO and market_details.get('insider_risk') == 'HIGH':
                signal_quality = 'STRONG'
                qualifies = True
                conviction_qualified += 1
                insider_qualified += 1
            # MEDIUM signal: High conviction OR (insider risk + cluster)
            elif conviction_ratio >= MIN_CONVICTION_RATIO:
                signal_quality = 'MEDIUM'
                qualifies = True
                conviction_qualified += 1
            elif insider_score >= 0.6:
                signal_quality = 'MEDIUM'
                qualifies = True
                insider_qualified += 1
            # Legacy signal: Old criteria (balance + bet size)
            elif balance >= MIN_WALLET_BALANCE and first_trade['amount'] >= MIN_BET_MARGIN:
                signal_quality = 'WEAK'
                qualifies = True
            
            if qualifies:
                # Fetch FULL market details for qualifying wallets
                print(f"   Fetching market details...")
                market_details = self.fetcher.get_market_details_full(first_trade.get('market_id', ''))
                
                bet_details = BetDetails(
                    amount=first_trade['amount'],
                    market_name=market_details.get('market_name'),
                    market_slug=market_details.get('market_slug'),
                    market_category=market_details.get('market_category'),
                    insider_risk=market_details.get('insider_risk', 'LOW'),
                    outcome=market_details.get('outcome'),
                    timestamp=first_trade['timestamp'],
                    tx_hash=first_trade['tx_hash']
                )
                
                wallet = Wallet(
                    address=address,
                    balance=balance,
                    first_bet=bet_details,
                    conviction_ratio=conviction_ratio,
                    insider_score=insider_score,
                    cluster_id=cluster_id,
                    signal_quality=signal_quality
                )
                qualifying_wallets.append(wallet)
                
                print(f"✓ {signal_quality} signal: {address[:10]}... "
                      f"(${balance:,.0f}, {conviction_ratio:.1%} conviction, "
                      f"{market_details.get('insider_risk')} risk)")
        
        # Sort by signal quality and insider score
        quality_order = {'STRONG': 3, 'MEDIUM': 2, 'WEAK': 1}
        qualifying_wallets.sort(
            key=lambda w: (quality_order[w.signal_quality], w.insider_score, w.conviction_ratio),
            reverse=True
        )
        
        print(f"\nSignal Summary:")
        print(f"  High-conviction plays: {conviction_qualified}")
        print(f"  Insider signals: {insider_qualified}")
        print(f"  Total qualifying: {len(qualifying_wallets)}")
        
        return qualifying_wallets
