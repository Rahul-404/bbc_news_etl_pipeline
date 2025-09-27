# Running Tests & Pre-commit

Testing ensures code quality and reliability. This project uses both **unit** and **integration** tests.

## Running Tests

Use `pytest` to run tests. You can run all tests or target specific types:

### Run All Tests

```bash
pytest
```

### Run Only Unit Tests

```bash
pytest tests/unit/
```

### Run Only Integration Tests

```bash
pytest tests/integration/
```

## Writing Tests

* All tests should be placed in the `tests/` directory.
* Test files should be named using the pattern: `test_*.py`

### Directory Structure

```
tests/
│
├── unit/             # Unit tests
│   └── test_*.py
│
├── integration/      # Integration tests
│   └── test_*.py
```

### Unit Tests

* Test individual functions or classes in isolation.
* Use mocking as needed to isolate components.
* Fast to run and should not rely on external systems (e.g., databases, APIs).

### Integration Tests

* Test interactions between multiple components or services.
* Use **Docker Compose** to spin up required services (e.g., databases, message queues).
* Tests run against these real service instances to validate integration.
* Slower than unit tests but ensure end-to-end component cooperation.

??? warning
    Integration tests depend on services started via **Docker Compose**.

    Before running integration tests, ensure Docker and Docker Compose are installed and running on your machine.

    Also, start required services with `docker-compose up -d` and stop them with `docker-compose down` after testing.

    Failing to do so may result in test failures or inconsistent test results.


### Running Integration Tests with Docker Compose

1. Define your services in a `docker-compose.yml` file at the project root. For example:

```yaml
version: '3.8'
services:
  db:
    image: postgres:13
    environment:
      POSTGRES_USER: testuser
      POSTGRES_PASSWORD: testpass
      POSTGRES_DB: testdb
    ports:
      - "5432:5432"
```

2. Start the services before running integration tests:

```bash
docker-compose up -d
```

3. Run integration tests:

```bash
pytest tests/integration/
```

4. After tests finish, stop and remove services:

```bash
docker-compose down
```

### Using Fixtures

* Use `pytest` fixtures to set up and tear down connections to services started by Docker Compose.
* You can also automate Docker Compose lifecycle within fixtures using Python subprocess calls or specialized libraries like `pytest-docker-compose`.

---
