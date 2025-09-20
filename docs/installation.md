# Installation

Follow these steps to set up the BBC News ETL Pipeline on your local machine or server.

## Prerequisites

- Python 3.10+
- Docker (optional, for containerized deployment)
- MongoDB or other NoSQL database

## Setup

1. Clone the repository:

```bash
git clone https://github.com/your-username/bbc-news-etl-pipeline.git
cd bbc-news-etl-pipeline
```

2. Create a virtual environment and activate it:


```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

Or if using Poetry:

```bash
poetry install
```

4. Configure environment variables (see [Configuration]()).

5. Run initial tests to verify setup:

```bash
pytest
```
