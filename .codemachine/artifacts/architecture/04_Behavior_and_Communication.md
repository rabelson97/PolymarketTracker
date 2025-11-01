<!-- anchor: api-design -->
### 3.7. API Design & Communication
**API Style:** Internal modules communicate via Python function calls and interfaces, while external interactions use RESTful HTTP calls (Polymarket API) and JSON-RPC (Polygon). No public API is exposed; the batch job offers a CLI entry point.

**Communication Patterns:** The orchestrator invokes synchronous request/response calls to fetch trades and wallet balances. Caching ensures idempotent processing, while structured events (JSON exports) can feed downstream systems asynchronously via files or optional message queues in future upgrades. Retry and backoff wrappers handle transient network errors.

**Key Interaction Flow (Sequence Diagram):** The following sequence illustrates a batch run detecting fresh wallets from recent trades, including balance and margin validation before reporting.

~~~plantuml
@startuml
actor Analyst
participant "CLI Orchestrator" as CLI
participant "Data Fetcher" as Fetcher
participant "Polymarket API" as API
participant "Wallet Analyzer" as Analyzer
participant "Polygon RPC" as RPC
participant "Cache/Storage" as Store
participant "Reporter" as Reporter

Analyst -> CLI : Configure run (lookback, thresholds)
CLI -> Fetcher : fetch_recent_trades()
Fetcher -> API : GET /trades?lookback
API --> Fetcher : Trades batch
Fetcher --> CLI : Normalized trades
CLI -> Analyzer : evaluate_wallets(trades)
Analyzer -> Store : check_wallet_history(address)
Store --> Analyzer : Prior activity (if any)
Analyzer -> RPC : get_balance(address)
RPC --> Analyzer : Balance (USD)
Analyzer -> Analyzer : calculate_margin(trade)
Analyzer -> Store : persist_snapshot(wallet)
Analyzer --> CLI : Qualifying wallets list
CLI -> Reporter : generate_reports(wallets)
Reporter -> Store : save_output(run_id)
Reporter --> Analyst : CSV/JSON summary
@enduml
~~~
