<!-- anchor: iteration-3-plan -->
### Iteration 3: Reporting, Orchestration & Quality Hardening

*   **Iteration ID:** `I3`
*   **Goal:** Finalize reporting outputs, orchestrator workflow, configuration polish, and quality gates to deliver a production-ready batch tool.
*   **Prerequisites:** `I1`, `I2`

<!-- anchor: task-i3-t1 -->
*   **Task 3.1:**
    *   **Task ID:** `I3.T1`
    *   **Description:** Implement reporter module for JSON/CSV exports and console summaries; author JSON Schema for report payloads in `docs/schemas/fresh_wallet_report.schema.json`; add unit tests for reporter formatting and schema validation.
    *   **Agent Type Hint:** `BackendAgent`
    *   **Inputs:** Reporting requirements from Section 2, Task `I2.T2` analyzer outputs.
    *   **Input Files:** [`src/polymarket_tracker/services/wallet_analyzer.py`, `docs/diagrams/wallet_evaluation_sequence.puml`]
    *   **Target Files:** [`src/polymarket_tracker/services/reporter.py`, `docs/schemas/fresh_wallet_report.schema.json`, `tests/test_reporter.py`, `data/exports/README.md`]
    *   **Deliverables:** Reporter capable of emitting JSON/CSV to `data/exports`, schema defining report structure, tests ensuring outputs match schema and formatting expectations, and brief README for export usage.
    *   **Acceptance Criteria:** Reporter tests pass; JSON Schema validates using `jsonschema`; generated files adhere to configuration thresholds and include required fields (address, balance, margin, timestamps).
    *   **Dependencies:** [`I2.T2`]
    *   **Parallelizable:** No

<!-- anchor: task-i3-t2 -->
*   **Task 3.2:**
    *   **Task ID:** `I3.T2`
    *   **Description:** Integrate Typer CLI orchestration wiring together fetcher, analyzer, storage, and reporter; provide CLI commands for `run-batch` with options for lookback and thresholds, and script entrypoint in `scripts/run_batch.py`.
    *   **Agent Type Hint:** `BackendAgent`
    *   **Inputs:** Tasks `I1.T3`, `I2.T1`, `I2.T3`, and `I3.T1` implementations.
    *   **Input Files:** [`src/polymarket_tracker/cli.py`, `src/polymarket_tracker/services/data_fetcher.py`, `src/polymarket_tracker/storage/cache_gateway.py`, `src/polymarket_tracker/services/reporter.py`]
    *   **Target Files:** [`src/polymarket_tracker/cli.py`, `scripts/run_batch.py`, `README.md`]
    *   **Deliverables:** Functional CLI command and helper script, updated README usage instructions, integration of configuration defaults and logging.
    *   **Acceptance Criteria:** Running `python -m polymarket_tracker.cli run-batch --dry-run` executes end-to-end with mocked deps; README includes command usage and configuration instructions; lints/tests remain passing.
    *   **Dependencies:** [`I3.T1`, `I2.T1`, `I2.T3`, `I1.T3`]
    *   **Parallelizable:** No

<!-- anchor: task-i3-t3 -->
*   **Task 3.3:**
    *   **Task ID:** `I3.T3`
    *   **Description:** Establish quality gates: configure CI workflow (GitHub Actions) with linting, tests, and OpenAPI/JSON Schema validation; add integration test using recorded fixtures; finalize documentation updates (CHANGELOG, success metrics notes).
    *   **Agent Type Hint:** `DevOpsAgent`
    *   **Inputs:** Tasks `I3.T2` CLI orchestration, `I2` modules, Section 5 verification strategy.
    *   **Input Files:** [`pyproject.toml`, `README.md`, `api/polymarket_client.yaml`, `docs/schemas/fresh_wallet_report.schema.json`]
    *   **Target Files:** [`.github/workflows/ci.yml`, `tests/integration/test_batch_run.py`, `CHANGELOG.md`, `README.md`]
    *   **Deliverables:** CI pipeline definition covering lint/test/spec validation, integration test with fixtures, changelog capturing initial release, README verification section.
    *   **Acceptance Criteria:** CI workflow runs lint/test/validate commands; integration test passes using mocked HTTP responses; documentation reflects verification steps and success metrics.
    *   **Dependencies:** [`I3.T2`, `I3.T1`]
    *   **Parallelizable:** No
