# Kubernetes Deployment (Helm/Kind)

### 1. Running on Kubernetes (Kind / Helm)

For a production-like deployment with scalability:

1. **Create a Kubernetes cluster (Kind example):**

```bash
kind create cluster --name bbc-news-etl
```

2. **Deploy Helm charts:**

```bash
helm install bbc-news-etl ./helm/bbc-news-etl
```

3. **Check pods and services:**

```bash
kubectl get pods
kubectl get svc
```

4. **Access Grafana (for monitoring):**

```bash
kubectl port-forward svc/grafana 3000:3000
```

---

### 2. Next Steps

* Explore **architecture/overview.md** for system design.
* Dive into **components/** for detailed ETL workflow.
* Check **configuration/** for environment variables and setup.
