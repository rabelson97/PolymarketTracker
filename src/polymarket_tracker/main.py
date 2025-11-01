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
            'first_bet_timestamp': w.first_bet_timestamp.isoformat()
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
        writer.writerow(['Address', 'Balance (USD)', 'First Bet Timestamp'])
        
        for w in wallets:
            writer.writerow([
                w.address,
                f"{w.balance:.2f}",
                w.first_bet_timestamp.isoformat()
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
            print(f"   First Bet: {wallet.first_bet_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Export results
        export_json(wallets)
        export_csv(wallets)
    else:
        print("\nNo qualifying wallets found in the lookback period.")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
