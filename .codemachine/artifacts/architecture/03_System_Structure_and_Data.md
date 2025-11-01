<!-- anchor: system-context -->
### 3.3. System Context Diagram (C4 Level 1)
**Description:** Illustrates how the Polymarket Fresh Wallet Tracker interacts with persona users and external services, highlighting data sources (Polymarket API, Polygon RPC) and outputs (reports/exports).

~~~plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

Person(analyst, "Market Analyst", "Consumes fresh wallet insights")
Person(trader, "Trader", "Monitors whale activity for strategy")
Person(researcher, "Researcher", "Exports data for further analysis")

System(polymarket_api, "Polymarket API", "Provides recent trades and market metadata")
System(polygon_rpc, "Polygon RPC / Node", "Supplies wallet balances (USDC on Polygon)")
System(research_tools, "External Analytics Tools", "Third-party tools using exported data")

System_Boundary(fwt_boundary, "Polymarket Fresh Wallet Tracker") {
  System(fwt_system, "Fresh Wallet Tracker", "Batch job identifying high-value new wallets")
}

Rel(analyst, fwt_system, "Runs batch job, reviews report", "CLI/Reports")
Rel(trader, fwt_system, "Requests exports", "CLI/Exports")
Rel(researcher, fwt_system, "Consumes data for research", "CSV/JSON")
Rel(fwt_system, polymarket_api, "Fetches recent trades & markets", "HTTPS/REST")
Rel(fwt_system, polygon_rpc, "Retrieves wallet balances", "HTTPS/Web3 RPC")
Rel(fwt_system, research_tools, "Provides exported datasets", "Files/ETL")

@enduml
~~~

<!-- anchor: container-diagram -->
### 3.4. Container Diagram (C4 Level 2)
**Description:** Details the primary runtime containers within the tracker, showing orchestration, processing, storage, and reporting components plus their interactions with external systems.

~~~plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

Person(analyst, "Market Analyst", "Triggers batch job")
System(polymarket_api, "Polymarket API", "Trades & markets")
System(polygon_rpc, "Polygon RPC", "Wallet balances")
System(research_tools, "Analytics Tools", "Consumes exports")

System_Boundary(fwt_boundary, "Polymarket Fresh Wallet Tracker") {
  Container(cli_runner, "Batch Orchestrator CLI", "Python/Typer", "Schedules and coordinates batch runs")
  Container(fetcher_service, "Data Fetcher", "Python module", "Calls Polymarket API and normalizes trades")
  Container(analyzer_service, "Wallet Analyzer", "Python module", "Evaluates wallet freshness and thresholds")
  ContainerDb(cache_store, "Cache & Storage", "SQLite / JSON", "Persists processed wallets & avoids duplication")
  Container(reporter_service, "Reporter", "Python module", "Generates JSON/CSV summaries and console output")
}

Rel(analyst, cli_runner, "Configures & executes", "CLI")
Rel(cli_runner, fetcher_service, "Invokes data ingestion", "Function call")
Rel(fetcher_service, polymarket_api, "Fetch recent trades", "HTTPS/REST")
Rel(analyzer_service, polygon_rpc, "Query wallet balance", "HTTPS/Web3")
Rel(cli_runner, analyzer_service, "Passes normalized trades", "Function call")
Rel(analyzer_service, cache_store, "Reads/writes cached wallet states", "SQL/IO")
Rel(analyzer_service, reporter_service, "Provides qualifying wallets", "In-memory data")
Rel(reporter_service, cache_store, "Stores outputs for reuse", "SQL/IO")
Rel(reporter_service, research_tools, "Exports files", "CSV/JSON")

@enduml
~~~

<!-- anchor: component-diagram -->
### 3.5. Component Diagram (C4 Level 3)
**Description:** Focuses on the Wallet Analyzer container, detailing core components and their interactions with supporting modules and external adapters.

~~~plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

Container(analyzer_service, "Wallet Analyzer", "Python module", "Evaluates trade records and wallet balances") {
  Component(trade_selector, "Trade Selector", "Python class", "Filters recent trades by lookback and deduplicates wallets")
  Component(freshness_evaluator, "Freshness Evaluator", "Python class", "Determines if wallet is placing its first bet")
  Component(margin_calculator, "Margin Calculator", "Python function", "Computes bet margin using trade metadata")
  Component(balance_checker, "Balance Checker", "Adapter", "Retrieves current wallet balance via Web3/Polymarket API")
  Component(cache_gateway, "Cache Gateway", "Repository", "Persists wallet snapshots in SQLite/JSON")
  Component(result_assembler, "Result Assembler", "Python class", "Builds qualifying wallet payloads for reporting")
}

Component(fetcher_adapter, "Trade Data Adapter", "HTTP Client", "Provides normalized trades from Data Fetcher")
Component(reporter_interface, "Reporter Interface", "Python protocol", "Receives qualifying wallets")

Rel(fetcher_adapter, trade_selector, "Supplies trade batch")
Rel(trade_selector, freshness_evaluator, "Passes candidate wallets")
Rel(freshness_evaluator, cache_gateway, "Checks prior wallet activity")
Rel(freshness_evaluator, margin_calculator, "Requests margin computation")
Rel(margin_calculator, result_assembler, "Sends margin outcome")
Rel(balance_checker, result_assembler, "Provides wallet balance")
Rel(result_assembler, cache_gateway, "Stores evaluated wallets")
Rel(result_assembler, reporter_interface, "Delivers qualifying wallets")

@enduml
~~~

<!-- anchor: data-model -->
### 3.6. Data Model Overview & ERD
**Description:** Defines core entities persisted or exchanged—wallets, bets, and cached snapshots—to support analysis and reporting.

**Key Entities:** Wallet, Bet, WalletSnapshot, RunMetadata.

~~~plantuml
@startuml
entity "Wallet" as Wallet {
  *address : string <<PK>>
  --
  created_at : datetime
  last_processed_at : datetime
}

entity "Bet" as Bet {
  *bet_id : string <<PK>>
  wallet_address : string <<FK>>
  market_id : string
  amount : decimal
  outcome : string
  margin : decimal
  timestamp : datetime
}

entity "WalletSnapshot" as Snapshot {
  *snapshot_id : integer <<PK>>
  wallet_address : string <<FK>>
  balance_usd : decimal
  first_bet_timestamp : datetime
  margin_at_entry : decimal
  recorded_at : datetime
}

entity "RunMetadata" as RunMeta {
  *run_id : string <<PK>>
  lookback_start : datetime
  lookback_end : datetime
  source : string
}

Wallet ||--o{ Bet : "places"
Wallet ||--o{ Snapshot : "captured by"
RunMeta ||--o{ Snapshot : "produces"

@enduml
~~~
