# Metrics (Prometheus)

The BBC News ETL Pipeline exposes **rich metrics via Prometheus** to provide real-time insights into pipeline performance, queue health, processing rates, and failures.

---

## 1. Overview

Prometheus collects metrics from **producers, consumers, and RabbitMQ**. Metrics allow:

* Monitoring **throughput** and **latency**.
* Tracking **queue depths** and **backlogs**.
* Alerting on **failures**, **DLQ accumulation**, or **resource saturation**.
* Observing **scaling behavior** when KEDA adjusts the number of producers/consumers.

---

## 2. Metrics Sources

| Component                   | Metrics Type    | Description                                                                            |
| --------------------------- | --------------- | -------------------------------------------------------------------------------------- |
| **Producers**               | Counter / Gauge | Number of article links scraped, success/failure counts, active tasks, work queue size |
| **Consumers (ETL Workers)** | Counter / Gauge | Messages consumed, ETL success/failure counts, retry attempts, DLQ counts              |
| **RabbitMQ**                | Queue metrics   | Task queue depth, DLQ depth, message publish/consume rate, queue latency               |
| **Kubernetes / KEDA**       | Custom metrics  | Pod replicas, CPU/Memory usage, scaling events                                         |

---

## 3. Example Metrics

### Producer Metrics

```text
bbc_producer_articles_scraped_total{section="world"} 1234
bbc_producer_scrape_failures_total{section="tech"} 12
bbc_producer_workqueue_length 15
```

### Consumer Metrics

```text
bbc_consumer_messages_processed_total 4567
bbc_consumer_etl_failures_total 34
bbc_consumer_dlq_messages_total 5
```

### RabbitMQ Metrics

```text
rabbitmq_queue_messages{queue="task_queue"} 120
rabbitmq_queue_messages{queue="dlq_queue"} 3
rabbitmq_queue_consumers 4
```

---

## 4. Integration

* **Prometheus Exporter** is embedded in each component (Python `prometheus_client`).
* Metrics are **scraped automatically** by the Prometheus server.
* Producers, Consumers, and RabbitMQ expose `/metrics` endpoints.

Example:

```python
from prometheus_client import start_http_server, Counter

articles_scraped = Counter('bbc_producer_articles_scraped_total', 'Total articles scraped')
start_http_server(8000)  # exposes /metrics
```

* Prometheus pulls metrics at a configurable interval (default: 15s).

---

## 5. Best Practices

* Use **meaningful labels** (e.g., `section`, `status`, `queue`) for filtering in Grafana.
* Set **alerts** for:

  * Work queue backlog > threshold
  * DLQ accumulation > threshold
  * ETL failure rate > threshold
* Combine **Prometheus metrics** with **Loki logs** for full observability.
* Ensure metrics endpoints are **secured** in production deployments.
