"""Main entry point for Polymarket Smart Money Tracker."""

import json
import csv
from datetime import datetime
from pathlib import Path
from .fetcher import PolymarketFetcher
from .analyzer import WalletAnalyzer


def export_json(wallets, output_path: str = "output/smart_money_signals.json"):
    """Export wallets to JSON format with signal data."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    data = [
        {
            'address': w.address,
            'balance': w.balance,
            'conviction_ratio': w.conviction_ratio,
            'insider_score': w.insider_score,
            'cluster_id': w.cluster_id,
            'signal_quality': w.signal_quality,
            'first_bet': {
                'amount': w.first_bet.amount,
                'market_name': w.first_bet.market_name,
                'market_category': w.first_bet.market_category,
                'insider_risk': w.first_bet.insider_risk,
                'market_slug': w.first_bet.market_slug,
                'market_url': f"https://polymarket.com/event/{w.first_bet.market_slug}" if w.first_bet.market_slug else None,
                'outcome': w.first_bet.outcome,
                'timestamp': w.first_bet.timestamp.isoformat(),
                'tx_hash': w.first_bet.tx_hash,
                'polygonscan_url': f"https://polygonscan.com/tx/{w.first_bet.tx_hash}"
            }
        }
        for w in wallets
    ]
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✓ Exported to {output_path}")


def export_csv(wallets, output_path: str = "output/smart_money_signals.csv"):
    """Export wallets to CSV format."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Signal Quality',
            'Address', 
            'Balance (USD)',
            'Conviction %',
            'Insider Score',
            'Cluster ID',
            'First Bet Amount',
            'Market Name',
            'Market Category',
            'Insider Risk',
            'Market URL',
            'Timestamp',
            'Transaction Hash'
        ])
        
        for w in wallets:
            market_url = f"https://polymarket.com/event/{w.first_bet.market_slug}" if w.first_bet.market_slug else ""
            writer.writerow([
                w.signal_quality,
                w.address,
                f"{w.balance:.2f}",
                f"{w.conviction_ratio:.1%}",
                f"{w.insider_score:.2f}",
                w.cluster_id or "",
                f"{w.first_bet.amount:.2f}",
                w.first_bet.market_name,
                w.first_bet.market_category or "",
                w.first_bet.insider_risk,
                market_url,
                w.first_bet.timestamp.isoformat(),
                w.first_bet.tx_hash
            ])
    
    print(f"✓ Exported to {output_path}")


def main():
    """Run the Polymarket Smart Money Tracker."""
    print("=" * 60)
    print("Polymarket Smart Money Tracker")
    print("Conviction + Insider Detection System")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Initialize components
    try:
        fetcher = PolymarketFetcher()
    except ValueError as e:
        print(f"[ERROR] {e}")
        print("\nPlease set ETHERSCAN_API_KEY environment variable")
        return
    
    analyzer = WalletAnalyzer(fetcher)
    
    # Find qualifying wallets
    wallets = analyzer.find_qualifying_wallets()
    
    # Display results
    print("\n" + "=" * 60)
    print(f"Found {len(wallets)} smart money signals")
    print("=" * 60)
    
    if wallets:
        # Group by signal quality
        strong = [w for w in wallets if w.signal_quality == 'STRONG']
        medium = [w for w in wallets if w.signal_quality == 'MEDIUM']
        weak = [w for w in wallets if w.signal_quality == 'WEAK']
        
        if strong:
            print(f"\n🔥 STRONG SIGNALS ({len(strong)}):")
            for i, w in enumerate(strong, 1):
                print(f"\n{i}. {w.address}")
                print(f"   Balance: ${w.balance:,.0f} | Conviction: {w.conviction_ratio:.1%} | Insider Score: {w.insider_score:.2f}")
                print(f"   Bet: ${w.first_bet.amount:,.0f} on {w.first_bet.timestamp.strftime('%Y-%m-%d %H:%M')}")
                print(f"   Market: {w.first_bet.market_name}")
                print(f"   Category: {w.first_bet.market_category} | Risk: {w.first_bet.insider_risk}")
                if w.cluster_id:
                    print(f"   ⚠️  Part of coordinated cluster: {w.cluster_id}")
                if w.first_bet.market_slug:
                    print(f"   🔗 https://polymarket.com/event/{w.first_bet.market_slug}")
                print(f"   📊 https://polygonscan.com/tx/{w.first_bet.tx_hash}")
        
        if medium:
            print(f"\n⚡ MEDIUM SIGNALS ({len(medium)}):")
            for i, w in enumerate(medium, 1):
                print(f"\n{i}. {w.address[:10]}... | ${w.balance:,.0f} | {w.conviction_ratio:.1%} conviction")
                print(f"   ${w.first_bet.amount:,.0f} on {w.first_bet.market_name[:60]}...")
                if w.cluster_id:
                    print(f"   Cluster: {w.cluster_id}")
        
        if weak:
            print(f"\n📊 WEAK SIGNALS ({len(weak)}): See CSV for details")
        
        # Export results
        export_json(wallets)
        export_csv(wallets)
    else:
        print("\nNo qualifying signals found in the lookback period.")
        print("Try adjusting thresholds in config.py")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
