# Configuration

The BBC News ETL Pipeline is highly configurable via **environment variables**, **configuration files**, and **Helm values**. This page documents all the key configuration options for **producers, consumers, message queues, storage, and observability**.

---

## 1. Environment Variables

Environment variables allow you to **customize behavior without modifying code**. Some key variables include:

### Producer / Scraper

| Variable          | Description                               | Default                       |
| ----------------- | ----------------------------------------- | ----------------------------- |
| `START_DATE`      | Start date for scraping (YYYY-MM-DD)      | `2025-01-01`                  |
| `CURRENT_DATE`    | Current date for work queue generation    | System date                   |
| `SCRAPE_INTERVAL` | Interval between scraping tasks (seconds) | `10`                          |
| `SELENIUM_URL`    | URL to connect to Selenium WebDriver      | `http://selenium:4444/wd/hub` |
| `RABBITMQ_HOST`   | RabbitMQ hostname                         | `rabbitmq`                    |
| `RABBITMQ_QUEUE`  | Task queue name                           | `task_queue`                  |
| `RABBITMQ_DLQ`    | Dead Letter Queue name                    | `dlq_queue`                   |

### Consumer / ETL Worker

| Variable        | Description                             | Default                           |
| --------------- | --------------------------------------- | --------------------------------- |
| `RABBITMQ_HOST` | RabbitMQ hostname                       | `rabbitmq`                        |
| `TASK_QUEUE`    | Name of task queue to consume           | `task_queue`                      |
| `DLQ_QUEUE`     | Name of DLQ                             | `dlq_queue`                       |
| `MONGO_URI`     | MongoDB connection string               | `mongodb://mongo:27017`           |
| `POSTGRES_URI`  | PostgreSQL connection string            | `postgresql://postgres:5432/news` |
| `MAX_RETRIES`   | Number of retries before sending to DLQ | `3`                               |

### Observability

| Variable              | Description                | Default                             |
| --------------------- | -------------------------- | ----------------------------------- |
| `PROMETHEUS_ENDPOINT` | URL for Prometheus metrics | `/metrics`                          |
| `LOKI_URL`            | Loki endpoint for logs     | `http://loki:3100/loki/api/v1/push` |
| `LOG_LEVEL`           | Logging level              | `INFO`                              |

---

## 2. Configuration Files

Some components support **YAML/JSON configuration files** for advanced settings:

* **`config/producers.yaml`**
  Configure sections to scrape, concurrency, and retries.
* **`config/consumers.yaml`**
  Define ETL transformation rules, batch size, and retry policies.
* **`config/helm/values.yaml`**
  Customize deployment settings for Kubernetes (resource limits, replicas, KEDA scaling, secrets).

---

## 3. Helm Chart Configuration

For Kubernetes deployments:

* **Replicas**: Scale producers and consumers based on queue depth using KEDA.
* **Resources**: Set CPU/memory limits and requests per pod.
* **Secrets**: Store database credentials, RabbitMQ credentials, and API keys securely.
* **Metrics & Logging**: Configure Prometheus scraping, Grafana dashboards, and Loki endpoints.

Example snippet from `values.yaml`:

```yaml
producers:
  replicas: 2
  seleniumUrl: http://selenium:4444/wd/hub
  startDate: 2025-01-01

consumers:
  replicas: 2
  maxRetries: 3

rabbitmq:
  host: rabbitmq
  taskQueue: task_queue
  dlqQueue: dlq_queue
```

---

## 4. Notes & Best Practices

* **Version control**: Keep `config/*.yaml` files under Git for reproducibility.
* **Environment separation**: Use different values for local, staging, and production environments.
* **Secrets**: Never hardcode passwords or API keys; use environment variables or Kubernetes secrets.
* **Dynamic scaling**: Configure KEDA triggers carefully to avoid over/under-provisioning producers and consumers.
