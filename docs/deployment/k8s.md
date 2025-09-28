# Kubernetes Deployment

This guide describes deploying the BBC News ETL pipeline in **production-like Kubernetes environments**, including KEDA autoscaling.

---

## Prerequisites

* Kubernetes cluster (Minikube, Kind, or cloud provider)
* Helm >= 3.x
* kubectl CLI
* Optional: KEDA for autoscaling

---

## Architecture

* **Primary Producer** → initializes work queue
* **Multiple Producers** → scrape articles, deduplicate, publish tasks
* **RabbitMQ** → message broker for Task Queue & DLQ
* **Consumers (ETL Workers)** → fetch and process tasks
* **MongoDB / PostgreSQL** → data storage
* **Prometheus / Grafana / Loki + Promtail** → observability
* **KEDA** → scales producers/consumers based on queue length

---

## Deployment Steps

1. Clone the repo:

```bash
git clone https://github.com/Rahul-404/bbc_news_etl_pipeline.git
cd bbc_news_etl_pipeline
```

2. Install RabbitMQ, MongoDB, PostgreSQL, Prometheus, Grafana, Loki using **Helm charts**:

```bash
helm install rabbitmq ./helm/rabbitmq
helm install mongo ./helm/mongodb
helm install postgres ./helm/postgres
helm install prometheus ./helm/prometheus
helm install grafana ./helm/grafana
helm install loki ./helm/loki
```

3. Deploy **Primary Producer, Producers, and Consumers**:

```bash
kubectl apply -f k8s/producers/
kubectl apply -f k8s/consumers/
```

4. Configure KEDA for **horizontal scaling**:

* Producers scale based on **Work Queue length**.
* Consumers scale based on **Task Queue depth**.
* Example KEDA ScaledObject YAML is included in `k8s/keda/`.

5. Verify Pods and Services:

```bash
kubectl get pods
kubectl get svc
```

6. Access dashboards:

* Grafana: http://<grafana-service-ip>:3000
* Prometheus: http://<prometheus-service-ip>:9090
* Loki: http://<loki-service-ip>:3100

---

## Notes

* Each Producer pod contains its own **Selenium driver** for scraping.
* DLQ handling is automatic: failed ETL messages remain in RabbitMQ for manual inspection.
* Logging and metrics are **fully integrated**, ready for production-grade monitoring.
* Helm charts allow **environment-specific configurations** via `values.yaml`.
