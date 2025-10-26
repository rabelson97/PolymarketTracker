#!/usr/bin/env python3
"""Track freshly activated Polymarket wallets with on-chain validation.

This script connects to Polymarket's public API, pulls recent trades, and filters
them using a few heuristics:

* The trade cash / margin must meet a minimum USD threshold.
* The trader must have held at least a target USDC balance at the trade's block.
* The wallet must be "fresh" (low historical Polygon transaction count).
* The trade must be the first Polymarket execution for the wallet.

Matched wallets are printed to stdout and can optionally be exported to CSV.

Environment variables
---------------------
``POLYGON_RPC_URL`` must point at a Polygon HTTPS RPC endpoint. The script only
reads chain state so any archive-capable endpoint (Alchemy, QuickNode, etc.)
works.  The Polymarket API currently requires an authenticated session cookie
to return trade payloads. Provide it via ``POLYMARKET_SESSION_TOKEN`` (the value
of the ``pm-access-token`` cookie) or the ``--session-token`` CLI flag. Without
it the API responds with ``{"ok": true}`` and the tracker exits early.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import sys
import time
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import requests
from requests import Response
from web3 import Web3
from web3.contract.contract import Contract


# Polygon USDC (6 decimals).
POLYGON_USDC = Web3.to_checksum_address("0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174")
USDC_DECIMALS = Decimal("1e6")


class TrackerError(RuntimeError):
    """Base error for tracker failures."""


class PolymarketAPIError(TrackerError):
    """Raised when the Polymarket API returns an unexpected payload."""


class ConfigurationError(TrackerError):
    """Raised for invalid runtime configuration."""


@dataclass(slots=True)
class TrackerConfig:
    """Holds runtime configuration supplied via CLI flags."""

    limit: int = 500
    min_cash: float = 5000.0
    min_balance: float = 50000.0
    fresh_max_prior_tx: int = 3
    csv_path: Optional[str] = None
    session_token: Optional[str] = None
    api_url: str = "https://polymarket.com/api/_a"


@dataclass(slots=True)
class Trade:
    """Normalized Polymarket trade payload."""

    wallet: str
    role: str
    transaction_hash: str
    block_number: int
    timestamp: dt.datetime
    cash_usd: float
    market: str
    outcome: str
    raw: Dict[str, object]


@dataclass(slots=True)
class WalletMatch:
    """Wallet that satisfies all screening criteria."""

    wallet: str
    transaction_hash: str
    block_number: int
    timestamp: dt.datetime
    cash_usd: float
    usdc_balance: float
    prior_tx_count: int
    market: str
    outcome: str
    role: str


def parse_args(argv: Optional[Sequence[str]] = None) -> TrackerConfig:
    """Parse command-line arguments into a :class:`TrackerConfig`."""

    parser = argparse.ArgumentParser(
        description="Polymarket Fresh-Whales Tracker",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--limit", type=int, default=500, help="Number of recent trades to scan")
    parser.add_argument(
        "--min-cash",
        type=float,
        default=5000.0,
        help="Minimum trade cash / margin in USD",
    )
    parser.add_argument(
        "--min-balance",
        type=float,
        default=50000.0,
        help="Minimum USDC balance at the trade block",
    )
    parser.add_argument(
        "--fresh-max-prior-tx",
        type=int,
        default=3,
        help="Maximum number of prior Polygon transactions for a wallet",
    )
    parser.add_argument(
        "--csv",
        type=str,
        default="",
        help="Optional CSV output path for matched wallets",
    )
    parser.add_argument(
        "--session-token",
        type=str,
        default="",
        help=(
            "Polymarket pm-access-token session cookie. If omitted, the tracker attempts to "
            "read POLYMARKET_SESSION_TOKEN from the environment."
        ),
    )
    parser.add_argument(
        "--api-url",
        type=str,
        default="https://polymarket.com/api/_a",
        help="Base URL for the Polymarket API proxy",
    )

    args = parser.parse_args(argv)
    csv_path = args.csv or None
    session_token = args.session_token or os.environ.get("POLYMARKET_SESSION_TOKEN") or None

    return TrackerConfig(
        limit=args.limit,
        min_cash=args.min_cash,
        min_balance=args.min_balance,
        fresh_max_prior_tx=args.fresh_max_prior_tx,
        csv_path=csv_path,
        session_token=session_token,
        api_url=args.api_url.rstrip("/"),
    )


def _coerce_float(value: object, default: Optional[float] = None) -> Optional[float]:
    """Convert various numeric encodings to ``float``."""

    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, str) and value.strip():
        try:
            return float(value)
        except ValueError:
            return default
    return default


def _parse_timestamp(value: object) -> Optional[dt.datetime]:
    """Best-effort parser for timestamps included in trade payloads."""

    if value is None:
        return None
    if isinstance(value, dt.datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=dt.timezone.utc)
        return value.astimezone(dt.timezone.utc)
    if isinstance(value, (int, float)):
        # Values from the API are seconds; anything too large is probably ms.
        if value > 1e12:
            value /= 1000.0
        return dt.datetime.fromtimestamp(value, tz=dt.timezone.utc)
    if isinstance(value, str) and value.strip():
        text = value.strip()
        for fmt in (dt.datetime.fromisoformat,):
            try:
                parsed = fmt(text.replace("Z", "+00:00"))
            except ValueError:
                continue
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=dt.timezone.utc)
            return parsed.astimezone(dt.timezone.utc)
    return None


def _clean_wallet(address: object) -> Optional[str]:
    """Return a checksum wallet address when possible."""

    if not isinstance(address, str):
        return None
    address = address.strip()
    if not address:
        return None
    try:
        return Web3.to_checksum_address(address)
    except ValueError:
        return None


class PolymarketClient:
    """Thin client for the Polymarket proxy API."""

    def __init__(self, base_url: str, session_token: Optional[str] = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": "fresh-whales-tracker/1.0",
            }
        )
        if session_token:
            # The pm-access-token cookie controls access to trade data.
            self.session.headers["Cookie"] = f"pm-access-token={session_token}"

    # ------------------------------------------------------------------
    # Low-level HTTP helpers
    # ------------------------------------------------------------------
    def _get(self, path: str, params: Optional[Dict[str, object]] = None) -> Dict[str, object]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        response: Response = self.session.get(url, params=params, timeout=30)
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise PolymarketAPIError(f"Polymarket API error: {exc}") from exc

        try:
            data = response.json()
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive
            raise PolymarketAPIError("Polymarket API returned invalid JSON") from exc

        # The API responds with {"ok": true} when the caller lacks a session cookie.
        if data == {"ok": True}:
            raise PolymarketAPIError(
                "Polymarket API returned an empty payload. Provide a valid pm-access-token "
                "cookie via POLYMARKET_SESSION_TOKEN or --session-token."
            )
        if not isinstance(data, dict):
            raise PolymarketAPIError("Unexpected Polymarket API response format")
        return data

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def fetch_recent_trades(self, limit: int) -> List[Trade]:
        """Return ``limit`` most recent trades as :class:`Trade` objects."""

        remaining = max(limit, 0)
        trades: List[Trade] = []
        cursor: Optional[str] = None
        seen_hashes: set[str] = set()

        while remaining > 0:
            page_size = min(remaining, 200)
            params: Dict[str, object] = {"limit": page_size}
            if cursor:
                params.update({"cursor": cursor})

            payload = self._get("orders/trades", params=params)
            entries, cursor = self._extract_trade_page(payload)
            if not entries:
                break

            for entry in entries:
                trade = self._normalize_trade(entry)
                if trade is None or trade.transaction_hash in seen_hashes:
                    continue
                trades.append(trade)
                seen_hashes.add(trade.transaction_hash)
                remaining -= 1
                if remaining <= 0:
                    break

            if cursor is None:
                break

        return trades

    def has_prior_trade(self, wallet: str, before: dt.datetime) -> bool:
        """Return ``True`` when the wallet traded before ``before``."""

        ts = int(before.timestamp())
        for params in (
            {"address": wallet, "limit": 1, "before": ts},
            {"address": wallet, "limit": 1, "beforeTimestamp": before.isoformat()},
            {"address": wallet, "limit": 1, "to": before.isoformat()},
        ):
            try:
                payload = self._get("orders/trades", params=params)
            except PolymarketAPIError:
                continue
            entries, _ = self._extract_trade_page(payload, allow_empty=True)
            if entries:
                return True
        return False

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _extract_trade_page(
        payload: Dict[str, object], allow_empty: bool = False
    ) -> Tuple[List[Dict[str, object]], Optional[str]]:
        """Return (rows, cursor) from a Polymarket trade response."""

        rows: List[Dict[str, object]] = []
        cursor: Optional[str] = None

        for key, value in payload.items():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                rows = [dict(item) for item in value]
            elif isinstance(value, dict) and "results" in value:
                maybe_rows = value.get("results")
                if isinstance(maybe_rows, list):
                    rows = [dict(item) for item in maybe_rows if isinstance(item, dict)]
                cursor_value = value.get("next") or value.get("cursor")
                if isinstance(cursor_value, str):
                    cursor = cursor_value
            elif key in {"next", "cursor"} and isinstance(value, str):
                cursor = value

        if not rows and not allow_empty:
            raise PolymarketAPIError(
                "Unable to locate trade list in Polymarket response."
            )
        return rows, cursor

    @staticmethod
    def _normalize_trade(entry: Dict[str, object]) -> Optional[Trade]:
        wallet = _clean_wallet(
            entry.get("taker")
            or entry.get("maker")
            or entry.get("userAddress")
            or entry.get("user")
        )
        if wallet is None:
            return None

        role = "taker" if wallet == _clean_wallet(entry.get("taker")) else "maker"

        tx_hash = entry.get("transactionHash") or entry.get("txHash") or entry.get("hash")
        if not isinstance(tx_hash, str) or not tx_hash:
            return None

        block_number = entry.get("blockNumber") or entry.get("block_number")
        try:
            block_int = int(block_number)
        except (TypeError, ValueError):
            return None

        timestamp = (
            _parse_timestamp(entry.get("timestamp"))
            or _parse_timestamp(entry.get("createdAt"))
            or _parse_timestamp(entry.get("created_at"))
        )
        if timestamp is None:
            return None

        cash_usd = _coerce_float(
            entry.get("cash")
            or entry.get("quoteAmount")
            or entry.get("value")
            or entry.get("quantityUsd")
        )
        if cash_usd is None:
            return None

        market_info = entry.get("market") or entry.get("event") or {}
        market = ""
        outcome = ""
        if isinstance(market_info, dict):
            market = str(
                market_info.get("question")
                or market_info.get("title")
                or market_info.get("name")
                or ""
            )
            outcome = str(
                market_info.get("outcome")
                or market_info.get("outcomeName")
                or market_info.get("outcome_ticker")
                or entry.get("outcome")
                or ""
            )
        else:
            market = str(entry.get("marketName") or entry.get("question") or "")
            outcome = str(entry.get("outcome") or entry.get("side") or "")

        return Trade(
            wallet=wallet,
            role=role,
            transaction_hash=str(tx_hash),
            block_number=block_int,
            timestamp=timestamp,
            cash_usd=float(cash_usd),
            market=market,
            outcome=outcome,
            raw=dict(entry),
        )


class WalletAnalyzer:
    """Performs on-chain checks for wallets."""

    def __init__(self, web3: Web3) -> None:
        self.web3 = web3
        self._erc20: Contract = self.web3.eth.contract(
            address=POLYGON_USDC,
            abi=[
                {
                    "constant": True,
                    "inputs": [{"name": "account", "type": "address"}],
                    "name": "balanceOf",
                    "outputs": [{"name": "", "type": "uint256"}],
                    "stateMutability": "view",
                    "type": "function",
                }
            ],
        )
        self._balance_cache: Dict[Tuple[str, int], float] = {}
        self._tx_count_cache: Dict[Tuple[str, int], int] = {}

    def usdc_balance(self, wallet: str, block_number: int) -> float:
        key = (wallet, block_number)
        if key in self._balance_cache:
            return self._balance_cache[key]

        try:
            raw_balance = self._erc20.functions.balanceOf(wallet).call(
                block_identifier=block_number
            )
        except Exception as exc:  # pragma: no cover - network errors
            raise TrackerError(f"Failed to fetch USDC balance for {wallet}: {exc}") from exc

        balance = float(Decimal(raw_balance) / USDC_DECIMALS)
        self._balance_cache[key] = balance
        return balance

    def prior_transaction_count(self, wallet: str, block_number: int) -> int:
        key = (wallet, block_number)
        if key in self._tx_count_cache:
            return self._tx_count_cache[key]

        try:
            count = self.web3.eth.get_transaction_count(wallet, block_number - 1)
        except Exception as exc:  # pragma: no cover
            raise TrackerError(
                f"Failed to fetch Polygon transaction count for {wallet}: {exc}"
            ) from exc

        self._tx_count_cache[key] = int(count)
        return int(count)


def connect_web3() -> WalletAnalyzer:
    rpc_url = os.environ.get("POLYGON_RPC_URL")
    if not rpc_url:
        raise ConfigurationError(
            "POLYGON_RPC_URL is not set. Export a Polygon HTTPS RPC endpoint before running."
        )

    web3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": 30}))
    if not web3.is_connected():
        raise ConfigurationError(
            "Unable to establish a connection to the Polygon RPC endpoint."
        )
    return WalletAnalyzer(web3)


def filter_trades(
    trades: Iterable[Trade],
    client: PolymarketClient,
    analyzer: WalletAnalyzer,
    config: TrackerConfig,
) -> List[WalletMatch]:
    matches: List[WalletMatch] = []
    for trade in trades:
        if trade.cash_usd < config.min_cash:
            continue

        try:
            balance = analyzer.usdc_balance(trade.wallet, trade.block_number)
        except TrackerError as exc:
            print(exc, file=sys.stderr)
            continue
        if balance < config.min_balance:
            continue

        try:
            prior_tx = analyzer.prior_transaction_count(trade.wallet, trade.block_number)
        except TrackerError as exc:
            print(exc, file=sys.stderr)
            continue
        if prior_tx > config.fresh_max_prior_tx:
            continue

        try:
            has_prior = client.has_prior_trade(trade.wallet, trade.timestamp - dt.timedelta(seconds=1))
        except PolymarketAPIError as exc:
            print(f"Skipping wallet {trade.wallet}: {exc}", file=sys.stderr)
            continue
        if has_prior:
            continue

        matches.append(
            WalletMatch(
                wallet=trade.wallet,
                transaction_hash=trade.transaction_hash,
                block_number=trade.block_number,
                timestamp=trade.timestamp,
                cash_usd=trade.cash_usd,
                usdc_balance=balance,
                prior_tx_count=prior_tx,
                market=trade.market,
                outcome=trade.outcome,
                role=trade.role,
            )
        )

    return matches


def emit_report(matches: Sequence[WalletMatch]) -> None:
    if not matches:
        print("No wallets matched the screening criteria.")
        return

    print("Matched wallets:")
    for match in matches:
        ts = match.timestamp.strftime("%Y-%m-%d %H:%M:%S %Z")
        print(
            f"- {match.wallet} | tx={match.transaction_hash} | block={match.block_number} | "
            f"cash=${match.cash_usd:,.2f} | USDC balance=${match.usdc_balance:,.2f} | "
            f"prior tx={match.prior_tx_count} | market={match.market or 'unknown'} | "
            f"outcome={match.outcome or 'unknown'}"
        )
        print(f"  role={match.role} | timestamp={ts}")


def export_csv(matches: Sequence[WalletMatch], csv_path: str) -> None:
    fieldnames = [
        "wallet",
        "transaction_hash",
        "block_number",
        "timestamp",
        "cash_usd",
        "usdc_balance",
        "prior_tx_count",
        "market",
        "outcome",
        "role",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for match in matches:
            writer.writerow(
                {
                    "wallet": match.wallet,
                    "transaction_hash": match.transaction_hash,
                    "block_number": match.block_number,
                    "timestamp": match.timestamp.isoformat(),
                    "cash_usd": f"{match.cash_usd:.2f}",
                    "usdc_balance": f"{match.usdc_balance:.2f}",
                    "prior_tx_count": match.prior_tx_count,
                    "market": match.market,
                    "outcome": match.outcome,
                    "role": match.role,
                }
            )
    print(f"Wrote {len(matches)} wallet(s) to {csv_path}")


def main(argv: Optional[Sequence[str]] = None) -> None:
    start_time = time.perf_counter()
    try:
        config = parse_args(argv)
        analyzer = connect_web3()
        client = PolymarketClient(config.api_url, config.session_token)
        trades = client.fetch_recent_trades(config.limit)
        matches = filter_trades(trades, client, analyzer, config)
        emit_report(matches)
        if config.csv_path:
            export_csv(matches, config.csv_path)
    except TrackerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        duration = time.perf_counter() - start_time
        print(f"Finished in {duration:.2f}s", file=sys.stderr)


if __name__ == "__main__":
    main()
