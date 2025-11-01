"""Main entry point for Polymarket Tracker."""

import json
import csv
from datetime import datetime
from pathlib import Path
from .fetcher import PolymarketFetcher
from .analyzer import WalletAnalyzer


def export_json(wallets, output_path: str = "output/qualifying_wallets.json"):
    """Export wallets to JSON format.
    
    Args:
        wallets: List of Wallet objects
        output_path: Output file path
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    data = [
        {
            'address': w.address,
            'balance': w.balance,
            'first_bet': {
                'amount': w.first_bet.amount,
                'market_name': w.first_bet.market_name,
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


def export_csv(wallets, output_path: str = "output/qualifying_wallets.csv"):
    """Export wallets to CSV format.
    
    Args:
        wallets: List of Wallet objects
        output_path: Output file path
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Address', 
            'Balance (USD)', 
            'First Bet Amount',
            'Market Name',
            'Outcome',
            'Market URL',
            'Timestamp',
            'Transaction Hash'
        ])
        
        for w in wallets:
            market_url = f"https://polymarket.com/event/{w.first_bet.market_slug}" if w.first_bet.market_slug else ""
            writer.writerow([
                w.address,
                f"{w.balance:.2f}",
                f"{w.first_bet.amount:.2f}",
                w.first_bet.market_name,
                w.first_bet.outcome,
                market_url,
                w.first_bet.timestamp.isoformat(),
                w.first_bet.tx_hash
            ])
    
    print(f"✓ Exported to {output_path}")


def main():
    """Run the Polymarket Fresh Wallet Tracker."""
    print("=" * 60)
    print("Polymarket Fresh Wallet Tracker")
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
    print(f"Found {len(wallets)} qualifying wallets")
    print("=" * 60)
    
    if wallets:
        print("\nQualifying Wallets:")
        for i, wallet in enumerate(wallets, 1):
            print(f"\n{i}. Address: {wallet.address}")
            print(f"   Balance: ${wallet.balance:,.2f}")
            print(f"   First Bet: ${wallet.first_bet.amount:,.2f} on {wallet.first_bet.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Market: {wallet.first_bet.market_name}")
            if wallet.first_bet.outcome != 'Unknown':
                print(f"   Outcome: {wallet.first_bet.outcome}")
            if wallet.first_bet.market_slug:
                print(f"   Market URL: https://polymarket.com/event/{wallet.first_bet.market_slug}")
            print(f"   Transaction: https://polygonscan.com/tx/{wallet.first_bet.tx_hash}")
        
        # Export results
        export_json(wallets)
        export_csv(wallets)
    else:
        print("\nNo qualifying wallets found in the lookback period.")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
