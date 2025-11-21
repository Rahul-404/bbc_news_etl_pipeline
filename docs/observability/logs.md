# Logs (Loki + Promtail)

Loki provides **centralized logging** for all components of the BBC News ETL pipeline. Promtail agents collect logs from each container/pod and send them to Loki for querying and visualization.

---

## 1. Overview

* Logs include **errors, retries, debug info, and operational events** from producers, consumers, and RabbitMQ.
* Loki integrates with **Grafana** to visualize logs alongside metrics.
* Promtail runs as a **sidecar or standalone agent** to collect container logs.

---

## 2. Log Sources

| Component           | Logs                                                                               |
| ------------------- | ---------------------------------------------------------------------------------- |
| Producers           | Scrape start/end, articles processed, retries, Selenium errors, task queue updates |
| Consumers           | ETL start/end, success/failure counts, DLQ messages, database errors               |
| RabbitMQ            | Message publish/consume events, queue depth alerts                                 |
| System / Kubernetes | Pod lifecycle events, scaling actions, resource metrics                            |

---

## 3. Log Format

* Structured logs in **JSON** are recommended for better querying.
* Example log entry from a producer:

```json
{
  "timestamp": "2025-09-28T12:00:00Z",
  "level": "INFO",
  "component": "producer",
  "section": "world",
  "articles_scraped": 15,
  "task_queue_length": 12
}
```

* Example log entry from a consumer:

```json
{
  "timestamp": "2025-09-28T12:01:00Z",
  "level": "ERROR",
  "component": "consumer",
  "etl_task_id": "abc123",
  "error": "PostgreSQL connection timeout",
  "retry_count": 2
}
```

---

## 4. Integration

* Promtail reads **container stdout/stderr**, **files**, or **systemd logs**.
* Sends logs to Loki over HTTP or gRPC endpoints.
* Grafana dashboards can **correlate logs with metrics** to identify pipeline bottlenecks.

---

## 5. Best Practices

* **Label logs** with `component`, `section`, `task_id`, and `environment` for filtering.
* Monitor **DLQ-related logs** to ensure no messages are lost.
* Use **retention policies** to manage storage.
* Secure Loki endpoints and use **role-based access control** for production environments.

```mermaid
flowchart TD

    A[Pipeline Run] -->|1 per pipeline| B[job_id]

    B --> C1[Worker / Pod 1]
    B --> C2[Worker / Pod 2]
    B --> C3[Worker / Pod 3]

    C1 -->|1 per worker| D1[context_id W1]
    C2 -->|1 per worker| D2[context_id W2]
    C3 -->|1 per worker| D3[context_id W3]

    D1 -->|Many tasks inside worker| T1a[task_id: Extract]
    D1 --> T1b[task_id: Transform]
    D1 --> T1c[task_id: Load]

    D2 --> T2a[task_id: Extract]
    D2 --> T2b[task_id: Transform]

    D3 --> T3a[task_id: Scrape URL]
    D3 --> T3b[task_id: Publish to Queue]
```
