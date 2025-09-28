# Components Overview

This page provides a **technical breakdown of each component** in the BBC News ETL pipeline.

---

## Components

- **Primary Producer & Scrapers**: Generate work queue, scrape BBC News articles, deduplicate, and push tasks to RabbitMQ.

- **Message Queue (RabbitMQ)**: Manages **Work Queue, Task Queue, and DLQ** for decoupling and reliability.

- **Consumers (ETL Workers)**: Fetch tasks, parse and transform raw HTML into structured datasets, store in MongoDB & PostgreSQL, and handle DLQ messages.

- **Storage Layer**:

    - **MongoDB**: raw/unstructured HTML.
    - **PostgreSQL**: cleaned, structured analytics-ready data.

- **Monitoring & Observability**: Prometheus metrics, Grafana dashboards, Loki logs (via Promtail).

- **Deployment & Orchestration**: Docker, Kubernetes + KEDA for autoscaling, Helm charts, CI/CD pipelines.

---

## 1. Producer (Scraper)

- **Purpose**: Generate work queue, scrape live and archived news articles, deduplicate against MongoDB, and publish tasks to RabbitMQ.

- **Implementation**:

    - Python 3.11 + `requests`, `BeautifulSoup4`, `Selenium`, `pika`.
    - Handles **rate limiting**, retries, and error logging via Promtail.

- **Key Features**:

    - Modular scrapers supporting multiple sections.
    - Work Queue orchestration based on dates and statistical thresholds.
    - Horizontally scalable via KEDA.

---

## 2. Message Queue (RabbitMQ)

- **Purpose**: Decouple producers and consumers while ensuring **reliable task delivery**.

- **Implementation**:

    - Maintains **Work Queue, Task Queue, DLQ**.
    - Durable queues with prefetch, acknowledgements, retries.

- **Key Features**:

    - Supports multiple producers and consumers.
    - Fault-tolerant messaging with DLQ for failed ETL tasks.
    - Prometheus metrics for queue depth, throughput, and failures.

---

## 3. Consumer (ETL Worker)

- **Purpose**: Transform raw HTML into structured datasets and load them into MongoDB/PostgreSQL.

- **Implementation**:

    - Python ETL scripts + `pandas`, `sqlalchemy`, `pymongo`.
    - Retry and DLQ integration for failed messages.

- **Key Features**:

    - Parallel and scalable processing via KEDA.
    - Metrics exposed to Prometheus; logs sent via Promtail → Loki.
    - Handles failed ETL tasks with DLQ for manual inspection.

---

## 4. Storage Layer

- **MongoDB**: Raw/unstructured HTML storage (data lake).

- **PostgreSQL**: Cleaned, analytics-ready datasets.

- **Features**:

    - Versioned datasets for reproducibility.
    - Optimized for query performance and downstream analytics.

---

## 5. Observability

- **Prometheus**: Collects metrics (queue depth, processing rates, error counts).
- **Grafana**: Dashboards visualize metrics and pipeline performance.
- **Loki + Promtail**: Centralized logging from all components for errors, retries, and debugging.

- **Features**:

    - Alerts for failures, bottlenecks, or anomalies.
    - Real-time monitoring for production-grade deployments.

---

## 6. Deployment & Orchestration

- **Docker**: Containerizes all components.
- **Kubernetes + KEDA**: Autoscaling, rolling updates, health checks.
- **Helm charts**: Simplify environment configuration and deployment.
- **CI/CD**: GitHub Actions for testing and automated deployment.
