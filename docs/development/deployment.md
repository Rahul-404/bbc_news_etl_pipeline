# Deployment Guide

This guide covers how to deploy the BBC News Scraper ETL Pipeline in two ways:

- Local deployment (for development and testing)
- Cloud deployment (for staging or production environments)

---

## 1. Local Deployment (Docker + Kubernetes on Docker Desktop)

### Overview

Local deployment is intended for development and testing. All services (databases, queues, monitoring) run as Docker containers, and the ETL pipeline runs inside a local Kubernetes cluster.

### Prerequisites

* Docker Desktop (with Kubernetes enabled)
* Terraform
* Helm
* kubectl
* git

### Components

| Component  | Tool       | Deployment Method |
| ---------- | ---------- | ----------------- |
| MongoDB    | Docker     | `docker-compose`  |
| PostgreSQL | Docker     | `docker-compose`  |
| RabbitMQ   | Docker     | `docker-compose`  |
| Prometheus | Docker     | `docker-compose`  |
| Loki       | Docker     | `docker-compose`  |
| Grafana    | Docker     | `docker-compose`  |
| ETL Jobs   | Kubernetes | Terraform / YAML  |
| Promtail   | Kubernetes | Terraform / YAML  |

### Folder Structure (recommended)

```
/deploy/local/
├── docker-compose.yml
├── terraform/
│   ├── main.tf
│   └── variables.tf
└── k8s/
    ├── worker-job.yaml
    ├── assigner-deployment.yaml
    └── promtail.yaml
```

### Steps

1. **Start infrastructure services:**

   ```bash
   docker-compose up -d
   ```

2. **Deploy Kubernetes resources:**

   ```bash
   cd deploy/local/terraform
   terraform init
   terraform apply
   ```

3. **Verify:**

   * Grafana: [http://localhost:3000](http://localhost:3000)
   * RabbitMQ: [http://localhost:15672](http://localhost:15672)
   * ETL logs via Grafana (Loki)

---

## 2. Cloud Deployment (AWS)

### Overview

Cloud deployment is designed for production or staging environments. The same architecture is deployed on AWS using managed services and Terraform for infrastructure.

### Services Used

| Component  | AWS Equivalent                          |
| ---------- | --------------------------------------- |
| MongoDB    | MongoDB Atlas / self-hosted on EC2      |
| PostgreSQL | Amazon RDS                              |
| RabbitMQ   | Amazon MQ / self-hosted                 |
| Kubernetes | Amazon EKS                              |
| Logs       | AWS CloudWatch / Loki                   |
| Metrics    | Amazon Managed Prometheus / self-hosted |
| Dashboard  | Grafana Cloud / EC2                     |

### Tools Required

* Terraform CLI
* AWS CLI (configured with credentials)
* kubectl
* Helm

### Folder Structure (recommended)

```
/deploy/aws/
├── terraform/
│   ├── main.tf
│   ├── eks-cluster.tf
│   ├── rds.tf
│   └── outputs.tf
└── k8s/
    ├── worker-job.yaml
    ├── assigner-deployment.yaml
    └── promtail.yaml
```

### Steps

1. **Provision infrastructure with Terraform:**

   ```bash
   cd deploy/aws/terraform
   terraform init
   terraform apply
   ```

2. **Configure kubectl:**

   ```bash
   aws eks update-kubeconfig --name my-cluster
   ```

3. **Deploy ETL components to EKS:**

   ```bash
   kubectl apply -f ../k8s/
   ```

4. **Access Monitoring Dashboards:**

   * Grafana Cloud or EC2 URL
   * AWS CloudWatch (if used for logs/metrics)

---
