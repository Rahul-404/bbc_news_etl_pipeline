# Dashboards (Grafana)

Grafana provides **real-time visualizations** of the BBC News ETL pipeline metrics collected by Prometheus. Dashboards allow developers and operators to **quickly assess pipeline health, throughput, and failures**.

---

## 1. Overview

* Grafana connects to **Prometheus** as the data source.
* Provides **custom dashboards** for producers, consumers, RabbitMQ, and overall pipeline performance.
* Dashboards are **pre-configured via JSON files** or Helm charts.
* Supports **alerts and notifications** (Slack, email, etc.) for critical conditions.

---

## 2. Example Dashboards

| Dashboard                    | Description                                                                               |
| ---------------------------- | ----------------------------------------------------------------------------------------- |
| **Producer Overview**        | Shows articles scraped, work queue length, scrape failures, and retries by section.       |
| **Consumer / ETL Dashboard** | Displays messages consumed, ETL success/failure counts, retry attempts, and DLQ messages. |
| **RabbitMQ Queue Status**    | Queue depth, message rate, DLQ count, consumer count.                                     |
| **Pipeline Health**          | Combined metrics for producers, consumers, and RabbitMQ, including scaling events (KEDA). |

---

## 3. Integration

* Grafana is included as a **Docker container** for local development or deployed via **Helm chart** in Kubernetes.
* Dashboards can be imported/exported using **JSON**.
* Use **templating variables** to switch between sections, queues, or environments dynamically.

---

## 4. Best Practices

* Keep **critical metrics at the top** for quick visibility.
* Configure **alerts** for DLQ accumulation, work queue backlog, or high ETL failure rate.
* Use **annotations** to mark deployments or incidents on dashboards.
* Combine **logs and metrics** for root-cause analysis.
