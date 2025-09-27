# Architecture Overview

The BBC News ETL Pipeline is designed with scalability, reliability, and maintainability in mind.

## Components

- **Scraper**: Extracts news articles from BBC News website using BeautifulSoup and Requests.
- **ETL Pipeline**: Processes and loads data into MongoDB.
- **Monitoring**: Uses Prometheus for metrics and Loki for logging.
- **Scheduler**: Apache Airflow orchestrates the pipeline tasks.

### Local Architecture

```mermaid
flowchart TD
  A[Work Assigner] --> B[RabbitMQ]
  B --> C[ETL Worker]
  C --> D[MongoDB]
  C --> E[PostgreSQL]
  C --> F[Promtail]
  F --> G[Loki]
  C --> H[Prometheus]
  I[Grafana] --> G
  I --> H
```

![Architecture Diagram](../assets/flowcharts/bbc_news_etl-local-dev-architecture_diagram.png)  <!-- Add your architecture diagram here -->
