<!-- anchor: cross-cutting -->
### 3.8. Cross-Cutting Concerns

<!-- anchor: authentication-authorization -->
#### 3.8.1. Authentication & Authorization
- Use API keys or OAuth tokens stored in parameter stores (e.g., AWS Secrets Manager) for Polymarket and Polygon RPC access.
- Restrict CLI execution to authorized operators via infrastructure ACLs or CI/CD credentials.
- Enforce principle of least privilege for any cloud IAM roles associated with the job.

<!-- anchor: logging-monitoring -->
#### 3.8.2. Logging & Monitoring
- Emit structured JSON logs with request identifiers and wallet processing counts.
- Aggregate logs via CloudWatch Logs or ELK for trend analysis; optionally forward to observability stack.
- Collect runtime metrics (job duration, API latency, error counts) with StatsD/OpenTelemetry exporters.

<!-- anchor: security-considerations -->
#### 3.8.3. Security Considerations
- Validate and sanitize external data, especially numeric fields when computing margins.
- Enforce TLS for all outbound calls; pin known endpoints where feasible.
- Automate dependency vulnerability scanning (Dependabot/Snyk) and track pinned versions.
- Rotate API credentials periodically and avoid persisting secrets in code or artifacts.

<!-- anchor: scalability-performance -->
#### 3.8.4. Scalability & Performance
- Keep processing stateless to allow horizontal scaling (multiple containers partitioning time windows).
- Batch API requests and reuse HTTP sessions to reduce latency.
- Use caching to avoid redundant balance checks and ensure incremental runs process only new trades.

<!-- anchor: reliability-availability -->
#### 3.8.5. Reliability & Availability
- Implement retry with exponential backoff for external calls, with circuit breaker thresholds.
- Persist intermediate snapshots enabling job restarts without reprocessing entire history.
- Configure health checks and alerts for job failures or data anomalies (e.g., zero trades processed).

<!-- anchor: deployment-view -->
### 3.9. Deployment View
- **Target Environment:** AWS (Fargate/ECS) or self-hosted container runner with access to internet endpoints.
- **Deployment Strategy:** Dockerized batch job triggered via AWS EventBridge schedule or cron, storing artifacts in S3 and cache in managed SQLite volume or AWS RDS (if multi-instance needed).

~~~plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Deployment.puml

DeploymentNode(aws_region, "AWS Region", "us-east-1") {
  DeploymentNode(eventbridge, "EventBridge Scheduler", "AWS EventBridge") {
    DeploymentNode(fargate_cluster, "Fargate Cluster", "AWS ECS Fargate") {
      ContainerInstance(batch_task, "Fresh Wallet Tracker Task", "Docker Container")
    }
  }
  DeploymentNode(data_layer, "Data Storage", "AWS S3 & Secrets Manager") {
    Node(s3_bucket, "S3 Bucket", "Stores reports & exports")
    Node(secrets_manager, "Secrets Manager", "Holds API keys")
  }
  DeploymentNode(externals, "External Services") {
    System(polymarket_api, "Polymarket API", "Trades & markets")
    System(polygon_rpc, "Polygon RPC", "Wallet balances")
  }
}

Rel(eventbridge, batch_task, "Triggers scheduled run")
Rel(batch_task, polymarket_api, "HTTPS requests")
Rel(batch_task, polygon_rpc, "JSON-RPC calls")
Rel(batch_task, s3_bucket, "Upload reports")
Rel(batch_task, secrets_manager, "Retrieve credentials")

@enduml
~~~
