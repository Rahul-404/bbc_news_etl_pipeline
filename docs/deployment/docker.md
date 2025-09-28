# Docker Deployment

This guide describes **how to run the BBC News ETL pipeline locally** using Docker Compose. Each component is containerized for portability and reproducibility.

---

## Prerequisites

* Docker >= 24.x
* Docker Compose >= 2.x
* Python 3.11 (for local development, optional if using pre-built images)

---

## Services Overview

The Docker Compose stack includes:

* **Primary Producer** → generates work queue
* **Producers** → scrape articles and push tasks
* **RabbitMQ** → message queue (Task Queue & DLQ)
* **Consumers (ETL Workers)** → fetch and transform messages
* **MongoDB** → raw data storage
* **PostgreSQL** → cleaned data storage
* **Prometheus** → metrics collection
* **Grafana** → dashboards
* **Promtail → Loki** → centralized logging

---

## Getting Started

1. Clone the repository:

```bash
git clone https://github.com/Rahul-404/bbc_news_etl_pipeline.git
cd bbc_news_etl_pipeline
```

2. Build Docker images (or pull pre-built images from registry):

```bash
docker-compose build
```

3. Start the stack:

```bash
docker-compose up -d
```

4. Verify services:

```bash
docker-compose ps
```

5. Access dashboards:

* Grafana: [http://localhost:3000](http://localhost:3000)
* Prometheus: [http://localhost:9090](http://localhost:9090)
* Loki: [http://localhost:3100](http://localhost:3100)

---

## Notes

* Each producer requires its own **Selenium driver instance**. Docker Compose sets up individual containers with separate drivers.
* Work queue initialization is handled by the **primary producer**.
* DLQ messages can be inspected via RabbitMQ management UI or by custom ETL scripts.
* Logs are forwarded via **Promtail → Loki** for centralized querying.
