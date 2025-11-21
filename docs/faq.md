# FAQ

This section answers **common questions and troubleshooting scenarios** for the BBC News ETL pipeline.

---

## General

**Q1. What is the purpose of this pipeline?**

A: To provide a **production-grade, scalable ETL pipeline** that scrapes BBC News articles, processes them into structured datasets, and stores them for analytics and downstream applications.

**Q2. Can I run this pipeline locally without Kubernetes?**

A: Yes. You can use the **Docker Compose setup** (`docker-compose.yml`) for local testing and development. Kubernetes is only required for production-grade deployments.

---

## Producers (Scrapers)

**Q3. Why do Producers need Selenium?**

A: Some BBC News pages use JavaScript rendering. Each Producer pod runs with its **own Selenium container** (e.g., `selenium/standalone-chrome`) to scrape such dynamic pages.

**Q4. How does the pipeline avoid duplicate articles?**

A: Before publishing messages, Producers check MongoDB for existing records. If articles already exist or counts meet a statistical threshold, they are skipped.

**Q5. How are scraping rates controlled?**

A: Scraping frequency is configurable via environment variables. Producers implement **rate limiting, retries, and exponential backoff** to prevent IP blocking.

---

## RabbitMQ

**Q6. What happens if RabbitMQ crashes?**

A: All queues are configured as **durable**, so messages persist even if RabbitMQ restarts.

**Q7. What is the Dead Letter Queue (DLQ)?**

A: Messages that fail after multiple retries are redirected to the **DLQ**. These must be inspected and retried manually to ensure no data loss.

---

## Consumers (ETL Workers)

**Q8. What if a Consumer fails while processing a message?**

A: RabbitMQ will requeue the message unless it repeatedly fails, in which case it is sent to the DLQ.

**Q9. Why are both MongoDB and PostgreSQL used?**

A:

* **MongoDB** stores raw HTML and unstructured data (data lake).
* **PostgreSQL** stores cleaned, analytics-ready datasets (data warehouse).

**Q10. Can I scale Consumers independently?**

A: Yes. RabbitMQ allows multiple Consumers to process messages in parallel. With Kubernetes + KEDA, Consumers auto-scale based on queue length.

---

## Observability

**Q11. Where can I see system health and metrics?**

A:

* **Grafana**: dashboards for queue depth, processing rate, error counts.
* **Prometheus**: raw metrics scraped from Producers, Consumers, and RabbitMQ.
* **Loki**: centralized logs (with Promtail as the agent).

**Q12. Why am I not seeing logs in Grafana Loki?**

A: Check that:

* `promtail` agents are running.
* Log paths are correctly mounted.
* Loki service is reachable from Promtail.

---

## Deployment

**Q13. How are Producers scaled automatically?**

A: The **primary Producer** creates a **work queue of dates**. Based on queue length, **KEDA scales additional Producers** to handle the load.

**Q14. How can I configure environment variables for different environments (dev, staging, prod)?**

A: Use Helm `values.yaml` files or `.env` files in Docker Compose.

**Q15. How do I rollback a failed deployment?**

A:

* With **Helm**: `helm rollback <release-name> <revision>`
* With **Docker Compose**: revert to the last known working image tag.

---

## Infrastructure

**Q16. Do I need cloud resources to run this?**

A: No. The pipeline can run locally with Docker Compose or Kubernetes (Kind/Minikube). Cloud infrastructure is optional but recommended for production.

**Q17. How is infrastructure provisioned?**

A: Using **Terraform** for declarative resource management (e.g., Kubernetes clusters, databases, networking).

---

## CI/CD

**Q18. How is documentation deployed automatically?**

A: GitHub Actions build the MkDocs site and deploy it to GitHub Pages whenever changes are pushed to `main`.

**Q19. How are Docker images versioned?**

A: Each Docker image is tagged with the Git commit SHA for traceability and reproducibility.

**Q20. What if my CI pipeline fails on `pre-commit` checks?**

A: Run `pre-commit run --all-files` locally to fix formatting and linting before pushing your changes.
