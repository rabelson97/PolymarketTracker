<!-- anchor: iteration-2-plan -->
### Iteration 2: Data Ingestion & Wallet Analysis Core

*   **Iteration ID:** `I2`
*   **Goal:** Implement trade ingestion, wallet analysis logic (freshness, margin), caching interfaces, and supporting sequence documentation guided by architectural artifacts.
*   **Prerequisites:** `I1`

<!-- anchor: task-i2-t1 -->
*   **Task 2.1:**
    *   **Task ID:** `I2.T1`
    *   **Description:** Build the Polymarket data fetcher service to retrieve and normalize recent trades; author OpenAPI v3 stub (`api/polymarket_client.yaml`) detailing used endpoints and payload schemas; add unit tests covering normalization logic.
    *   **Agent Type Hint:** `BackendAgent`
    *   **Inputs:** Section 2 Key Components, Task `I1.T3` adapter stubs.
    *   **Input Files:** [`src/polymarket_tracker/adapters/polymarket_client.py`, `docs/configuration.md`]
    *   **Target Files:** [`src/polymarket_tracker/services/data_fetcher.py`, `api/polymarket_client.yaml`, `tests/test_data_fetcher.py`]
    *   **Deliverables:** Fetcher module with functions to pull trades within lookback, normalized trade dataclass, validated OpenAPI stub, and unit tests with mocked responses.
    *   **Acceptance Criteria:** Tests pass via `pytest tests/test_data_fetcher.py`; OpenAPI file validates with `speccy`/`openapi-spec-validator`; code adheres to linting and uses typed dataclasses/enums per plan.
    *   **Dependencies:** [`I1.T3`]
    *   **Parallelizable:** No

<!-- anchor: task-i2-t2 -->
*   **Task 2.2:**
    *   **Task ID:** `I2.T2`
    *   **Description:** Implement wallet analyzer logic covering freshness determination, margin computation, and orchestration of balance checks; generate PlantUML sequence diagram documenting the evaluation flow and store it at `docs/diagrams/wallet_evaluation_sequence.puml`.
    *   **Agent Type Hint:** `BackendAgent`
    *   **Inputs:** Section 2 Key Components, Task `I2.T1` normalized trade outputs, Task `I1.T2` diagrams.
    *   **Input Files:** [`src/polymarket_tracker/services/data_fetcher.py`, `src/polymarket_tracker/adapters/balance_provider.py`, `docs/diagrams/component_overview.puml`]
    *   **Target Files:** [`src/polymarket_tracker/services/wallet_analyzer.py`, `docs/diagrams/wallet_evaluation_sequence.puml`, `tests/test_wallet_analyzer.py`]
    *   **Deliverables:** Analyzer module with functions/classes to evaluate wallet freshness, compute margin, request balances; up-to-date sequence diagram; unit tests covering margin thresholds and caching interactions (using mocks).
    *   **Acceptance Criteria:** Tests pass (`pytest tests/test_wallet_analyzer.py`); sequence diagram renders without syntax errors and aligns with Section 2 communication patterns; code respects thresholds defined in configuration.
    *   **Dependencies:** [`I2.T1`, `I1.T3`]
    *   **Parallelizable:** No

<!-- anchor: task-i2-t3 -->
*   **Task 2.3:**
    *   **Task ID:** `I2.T3`
    *   **Description:** Develop the storage layer (SQLite repository) for wallet snapshots and run metadata, including SQL schema initialization, CRUD helpers, and caching interface integration with analyzer.
    *   **Agent Type Hint:** `DatabaseAgent`
    *   **Inputs:** Data model overview (Section 2) and Task `I2.T2` analyzer requirements.
    *   **Input Files:** [`src/polymarket_tracker/services/wallet_analyzer.py`, `docs/diagrams/data_model.mmd`]
    *   **Target Files:** [`src/polymarket_tracker/storage/cache_gateway.py`, `src/polymarket_tracker/storage/models.py`, `data/cache.sqlite`, `tests/storage/test_cache_gateway.py`]
    *   **Deliverables:** Database schema definitions, repository functions, migration/init script, and tests validating persistence and retrieval of wallet snapshots.
    *   **Acceptance Criteria:** Tests in `tests/storage/test_cache_gateway.py` succeed using temporary SQLite; schema mirrors ERD relationships; analyzer integrates without unresolved imports; no direct coupling to external APIs.
    *   **Dependencies:** [`I2.T2`]
    *   **Parallelizable:** No
