# BBC News Pipeline: Production-Grade Data Ingestion & ETL
![CI](https://github.com/Rahul-404/bbc_news_etl_pipeline/actions/workflows/publish-docs.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/github/license/Rahul-404/bbc_news_etl_pipeline)

## Overview

This repository contains a production-grade pipeline to scrape BBC News (both live and archived articles), process them into analytics-ready records and store them for downstream use. The pipeline is built to run on Kubernetes with horizontally-scalable producers and consumers, robust observability (Prometheus, Grafana, Loki), and reliable message delivery via RabbitMQ.

Goals:

- Reliable: durable queues, retry and DLQ patterns
- Scalable: producers & consumers autoscalable on K8s
- Observable: metrics, traces (optional), logs centralised in Loki
- Portable: containerized components, IaC for cloud infra
- Reproducible: deterministic ETL with versioned pipelines

---

This project demonstrates how to design a **real-world end-to-end data engineering system** that is robust, scalable, and production-ready.

---

Quick links:

- [mkdocs.yml]() — site config
- [docs/]() — the markdown pages in this documentation
- [helm/]() — Helm charts for deployment
- [k8s/]() — base Kubernetes manifests
- [docker/]() — Dockerfile sample for services

---
