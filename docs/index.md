# BBC News Pipeline: Production-Grade Data Ingestion & ETL
![CI](https://github.com/Rahul-404/bbc_news_etl_pipeline/actions/workflows/publish-docs.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/github/license/Rahul-404/bbc_news_etl_pipeline)


## Overview

The **BBC News Pipeline** is a **data engineering project** designed as a **production-grade pipeline** for scalable news ingestion and transformation.

It automates the process of:

- Scraping live BBC News articles
- Storing raw JSON documents in **MongoDB**
- Running ETL workflows with **Apache Airflow**
- Loading cleaned, structured datasets into **PostgreSQL**
- Monitoring system health and performance with **Prometheus, Grafana, Loki, and Promtail**
- Containerized and deployed using **Docker** and **Kubernetes**
- Provisioned via **Terraform** for Infrastructure as Code (IaC)

This project demonstrates how to design a **real-world end-to-end data engineering system** that is robust, scalable, and production-ready.

---

## Features
- **Data Ingestion:** Web scraper for BBC News articles
- **Raw Data Lake:** Semi-structured JSON storage in MongoDB
- **ETL Pipeline:** Transformation & cleaning with Apache Airflow
- **Data Warehouse Layer:** Structured, analytics-ready tables in PostgreSQL
- **Monitoring:** Logs and metrics with Prometheus, Grafana, Loki, Promtail
- **Infrastructure:** Modular, containerized services with Docker, Kubernetes & Terraform

---

## Repository Structure
```bash
bbc-news-etl-pipeline/
│
├── docs/                  # MkDocs documentation
├── scraper/               # BBC web scraping scripts
├── airflow_dags/          # ETL workflows
├── configs/               # Configurations (Prometheus, Loki, etc.)
├── docker/                # Dockerfiles for services
├── k8s/                   # Kubernetes manifests
├── terraform/             # IaC for provisioning infra
└── README.md              # Quick project overview
```
