<!-- anchor: design-rationale -->
## 4. Design Rationale & Trade-offs

<!-- anchor: key-decisions -->
### 4.1. Key Decisions Summary
- Chose modular batch architecture to satisfy non-real-time scope while preserving future extensibility.
- Selected Python ecosystem for alignment with requirements, available SDKs, and rapid iteration.
- Implemented lightweight SQLite/JSON caching over heavier databases to minimize operational overhead.
- Employed structured logging and configuration management to ease troubleshooting and environment parity.

<!-- anchor: alternatives -->
### 4.2. Alternatives Considered
- **Real-time Streaming Pipeline (e.g., Kafka + Flink):** Rejected due to complexity and explicit non-goal of real-time monitoring.
- **Managed Data Warehouse (e.g., BigQuery, Snowflake):** Deferred; unnecessary for current batch analytics volume.
- **Serverless-only Approach (AWS Lambda):** Limited by execution timeouts for larger batches; container batch offers more control.

<!-- anchor: risks-mitigation -->
### 4.3. Known Risks & Mitigation
- **API Rate Limits:** Mitigate with adaptive batching, caching, and scheduled runs during off-peak windows.
- **Definition Ambiguity for Margin:** Document assumptions, parameterize margin formula, and validate with domain experts.
- **External API Schema Changes:** Encapsulate clients behind adapters and enforce contract tests.
- **On-chain Data Latency:** Introduce retry/backoff and consider multiple RPC providers for redundancy.

<!-- anchor: future-considerations -->
## 5. Future Considerations

<!-- anchor: potential-evolution -->
### 5.1. Potential Evolution
- Integrate real-time event streaming and alerting via websockets or message queues.
- Add dashboard visualization layer (e.g., Streamlit) for interactive exploration.
- Extend analytics to track wallet performance over time and correlate with market outcomes.

<!-- anchor: deeper-dive -->
### 5.2. Areas for Deeper Dive
- Formalize margin calculation definition with Polymarket domain experts.
- Benchmark API throughput to size batch schedules and concurrency.
- Design schema migration strategy if moving from SQLite to scalable relational storage.

<!-- anchor: glossary -->
## 6. Glossary
- **Fresh Wallet:** Wallet placing its first recorded bet within the configured lookback window.
- **Margin:** Difference between initial stake and potential payout (configurable calculation method).
- **Snapshot:** Persisted record of wallet state (balance, margin, timestamps) at processing time.
- **Lookback Window:** Time span for evaluating new trades during batch runs.
