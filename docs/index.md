# BBC News Pipeline: Production-Grade Data Ingestion & ETL
![CI](https://github.com/Rahul-404/bbc_news_etl_pipeline/actions/workflows/publish-docs.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/github/license/Rahul-404/bbc_news_etl_pipeline)


## Overview

This repository hosts a **production-grade data engineering pipeline** designed to scrape BBC News (live and archived articles), transform the data into analytics-ready formats, and store it for downstream consumption. The pipeline is **containerized**, runs seamlessly on **Kubernetes**, and incorporates **robust observability** and **reliable messaging** patterns.

Key features include:

* **Reliable** – Durable queues, retry mechanisms, and Dead Letter Queue (DLQ) support for fault-tolerant message delivery.
* **Scalable** – Horizontally scalable producers and consumers orchestrated via Kubernetes.
* **Observable** – Centralized metrics, logs, and dashboards using Prometheus, Grafana, and Loki.
* **Portable** – Fully containerized components with infrastructure-as-code (Terraform & Helm) for cloud portability.
* **Reproducible** – Deterministic ETL pipelines with versioned data and modular architecture.

This project demonstrates the design of a **real-world end-to-end data engineering system** that balances **scalability, reliability, and maintainability** – perfect for showcasing as a **portfolio-grade project**.

---

## Architecture Highlights

* **Producers**: Scrape live & archived BBC News articles using Python & BeautifulSoup.
* **Message Queue**: RabbitMQ for decoupled communication and reliable message handling.
* **Consumers / ETL Workers**: Transform raw HTML content into structured, analytics-ready records.
* **Storage**: MongoDB for raw/unstructured data, PostgreSQL for structured, cleaned datasets.
* **Observability**: Prometheus metrics, Grafana dashboards, and Loki logs for monitoring and troubleshooting.
* **Deployment**: Containerized services orchestrated via Kubernetes with Helm charts and CI/CD automation.

<!-- *Optional:* Tracing can be added for end-to-end observability of pipeline execution. -->

---

## Quick Links

* [mkdocs.yml](#) — Site configuration for documentation
* [docs/](#) — Markdown pages with detailed explanations
* [helm/](#) — Helm charts for deploying services on Kubernetes
* [k8s/](#) — Base Kubernetes manifests for each service
* [docker/](#) — Dockerfiles for containerizing pipeline components
* [README.md](#) — Project overview and instructions

---

### Why this project matters

This project is **portfolio-ready** because it demonstrates:

* **Full-stack data engineering skills** – ETL, message queues, database design, monitoring, and deployment.
* **Production-grade design patterns** – scalability, observability, reliability, and reproducibility.
* **Cloud-native approach** – Kubernetes, Helm, Docker, and Terraform integration.

It’s an ideal showcase for **data engineering roles**, demonstrating your ability to handle **end-to-end data pipelines in a real-world environment**.
