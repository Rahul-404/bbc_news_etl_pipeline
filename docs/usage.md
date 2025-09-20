# Usage

This section explains how to run and interact with the BBC News ETL Pipeline.

## Running the Scraper

```bash
python src/scraper/main.py
```

This will start the scraper, extract the latest news articles, and store them in the database.

## Running the ETL Pipeline

The ETL pipeline automates data extraction, transformation, and loading.

```bash
python src/etl_pipeline/main.py
```


## Monitoring

The pipeline integrates with Prometheus and Loki for monitoring and logging.

- Access Prometheus dashboard at `http://localhost:9090`

- Access Grafana dashboard (if set up) at `http://localhost:3000`
