<!-- anchor: verification-and-integration-strategy -->
## 5. Verification and Integration Strategy

<!-- anchor: testing-levels -->
*   **Testing Levels:** Unit tests for fetcher, analyzer, reporter, and storage modules in respective iterations; integration test in `I3.T3` simulating end-to-end batch run with mocked APIs; optional manual dry-run validation against sandbox data prior to production scheduling.

<!-- anchor: cicd -->
*   **CI/CD:** GitHub Actions pipeline (established in `I3.T3`) executing linting (`ruff`/`flake8`), type checks (`mypy`), unit/integration tests, OpenAPI validation, JSON Schema validation, and packaging smoke tests; artifacts (coverage, reports) uploaded for review.

<!-- anchor: code-quality-gates -->
*   **Code Quality Gates:** Enforce zero lint errors, maintain ≥90% unit test coverage for analyzer logic, ensure type hints on public interfaces, and require successful schema validations before merge.

<!-- anchor: artifact-validation -->
*   **Artifact Validation:** PlantUML/Mermaid diagrams checked via CLI render scripts; OpenAPI stub validated against official schema; JSON Schema tested using representative payloads; configuration documentation peer-reviewed for completeness.

<!-- anchor: glossary -->
## 6. Glossary

*   **Fresh Wallet:** Wallet whose first recorded bet falls within the configured lookback window and meets minimum thresholds.
*   **Margin:** Difference between wager amount and potential payout for a single bet, used to filter qualifying wallets.
*   **Wallet Snapshot:** Persisted record capturing wallet balance, first bet timestamp, margin, and run metadata to prevent duplicate processing.
*   **Lookback Window:** Configurable duration (default 7 days) determining the range of trades evaluated in each batch run.
*   **Dry Run:** Execution mode that uses mocked or cached data to validate processing logic without live API calls or state mutations.
