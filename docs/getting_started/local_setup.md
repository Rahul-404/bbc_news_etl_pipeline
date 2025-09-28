# Local Setup (Docker Compose)

### 1. Running Locally with Docker Compose

This method runs all services (Producer, Consumer, RabbitMQ, MongoDB, PostgreSQL) in containers for quick testing.

1. Build Docker images:

```bash
docker compose build
```

2. Start the services:

```bash
docker compose up -d
```

3. Verify services are running:

```bash
docker compose ps
```

4. Stop services when done:

```bash
docker compose down
```

---

### 2. Run Tests & Pre-commit Hooks

Ensure code quality and reliability:

```bash
# Run unit tests
pytest tests/

# Run pre-commit checks
pre-commit run --all-files
```

---

### 3. Next Steps

* Explore **architecture/overview.md** for system design.
* Dive into **components/** for detailed ETL workflow.
* Check **configuration/** for environment variables and setup.
