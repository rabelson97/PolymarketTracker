<!-- anchor: proposed-architecture -->
## 3. Proposed Architecture

<!-- anchor: architectural-style -->
### 3.1. Architectural Style
Adopt a modular batch-oriented layered architecture with hexagonal influences: an orchestration layer coordinates ingestion, analysis, and reporting while isolating infrastructure adapters (Polymarket API client, Polygon RPC, storage) from domain logic. This style supports clear separation of concerns, simplifies testing via ports/adapters, and allows future migration toward streaming or microservices if higher frequency monitoring becomes necessary.

<!-- anchor: technology-stack -->
### 3.2. Technology Stack Summary
| Layer | Technology | Rationale |
| --- | --- | --- |
| Orchestration & CLI | Python 3.11, Typer/Click | Mature ecosystem, straightforward scripting, CLI ergonomics. |
| API Integration | `requests`, `py-clob-client` (Polymarket), `web3.py` | Reliable HTTP client; Polymarket-specific SDK; on-chain balance retrieval via Polygon RPC. |
| Data Processing | Native Python, `pandas` (optional) | Lightweight transformations; `pandas` assists with research exports when needed. |
| Caching/Storage | SQLite (via `sqlite3`) or JSON file | Embedded, zero-ops storage; simple interchange for batch jobs. |
| Configuration | `python-dotenv`, environment variables | Externalizes secrets, supports multiple environments. |
| Testing | `pytest`, `responses` | Unit testing for analysis logic and API mocks. |
| Packaging | Poetry or pip/requirements.txt | Dependency management and reproducible environments. |
| Deployment | Docker, cron/serverless scheduler | Containerization enables reproducible batch jobs; scheduling suits periodic runs. |
| Observability | Structured logging (`structlog`/`logging`), optional OpenTelemetry hooks | Facilitates troubleshooting and future integration with monitoring stacks. |
