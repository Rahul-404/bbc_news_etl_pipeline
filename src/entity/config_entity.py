import os
import platform
from dataclasses import dataclass
from datetime import datetime
from typing import Tuple

from dotenv import load_dotenv

load_dotenv()

# --- Clients Configs ---

@dataclass
class MongoDBConfig:
    """
    Configuration for MongoDB connection and document schema.

    Environment Variables
    ---------------------
    MONGODB_DATABASE_NAME : str
        Name of the MongoDB database (default: 'BBC_NEWS_DATABASE').

    MONGODB_DATA_COLLECTION_NAME : str
        Name of the MongoDB data collection (default: 'RAW_BBC_NEWS_COLLECTION').

    Attributes
    ----------
    MONGODB_DATABASE_NAME : str
        MongoDB database name.

    MONGO_DOC_DATE_KEY : str
        Key name for the document's published date (default: 'published').

    MONGO_DOC_CATEGORY_KEY : str
        Key name for the document's category field (default: 'category').

    MONGO_DOC_SUB_CATEGORY_KEY : str
        Key name for the document's sub-category field (default: 'sub_category').

    MONGO_DOC_ARTICLE_URL_KEY : str
        Key name for the document's article URL (default: 'url').
    """
    MONGODB_SERVICE_NAME: str = os.getenv("MDB_SERVICE_NAME", "MongoDBService")
    MONGODB_DATABASE_NAME: str = os.getenv("MDB_DATABASE_NAME", "BBC_NEWS_DATABASE")
    MONGODB_DATA_COLLECTION_NAME: str = os.getenv("MDB_DATA_COLLECTION_NAME", "RAW_BBC_NEWS_COLLECTION")
    MONGODB_BACKUP_DATA_COLLECTION_NAME: str = os.getenv("MDB_BACKUP_DATA_COLLECTION_NAME", "BACKUP_BBC_NEWS_COLLECTION")
    MONGODB_JOB_COLLECTION_NAME: str = os.getenv("MDB_JOB_COLLECTION_NAME", "BBC_JOB_COLLECTION")
    MONGODB_FAILED_JOB_COLLECTION_NAME: str = os.getenv("MDB_FAILED_JOB_COLLECTION_NAME", "BBC_FAILED_JOB_COLLECTION")
    MONGODB_FAILED_TASK_COLLECTION_NAME: str = os.getenv("MODB_FAILED_TASK_COLLECTION_NAME", "BBC_FAILED_TASK_COLLECTION")
    MONGODB_WORK_CHECKPOINT_NAME: str = os.getenv("MDB_WORK_CHECKPOINT_NAME", "WORK_CHECKPOINT")
    MONGO_DOC_DATE_KEY: str = "published"
    MONGO_DOC_CATEGORY_KEY: str = "category"          # Fixed typo here
    MONGO_DOC_SUB_CATEGORY_KEY: str = "sub_category"  # Fixed typo here
    MONGO_DOC_ARTICLE_URL_KEY: str = "url"
    MONGO_HOST: str = os.getenv("MONGO_HOST", "localhost")
    MONGO_PORT: int = int(os.getenv("MONGO_PORT", 27017))
    MONGODB_URI: str = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0

@dataclass
class RabbitMQConfig:
    """
    Configuration for RabbitMQ connection.

    Environment Variables
    ---------------------
    RABBITMQ_HOST : str
        RabbitMQ host address (default: 'localhost').

    RABBITMQ_PORT : int
        RabbitMQ port number (default: 5672).

    RABBITMQ_VHOST : str
        Virtual host for RabbitMQ (default: '/').

    RABBITMQ_QUEUE_NAME : str
        Name of the RabbitMQ queue to use (default: 'bbc_news_tasks').

    RABBITMQ_USER : str
        RabbitMQ username (default: 'guest').

    RABBITMQ_PASSWORD : str
        RabbitMQ password (default: 'guest').

    Attributes
    --------------
    RABBITMQ_URL : str
        Constructed AMQP URL in the form:
        "amqp://<user>:<password>@<host>:<port>/"

    RETRIES : int
        Number of connection retry attempts. Default: 5.
    """
    RABBITMQ_SERVICE_NAME: str = os.getenv("RMQ_SERVICE_NAME", "RabbitMQService")
    RABBITMQ_HOST_NAME: str = os.getenv("RMQ_HOST_NAME", "localhost")
    RABBITMQ_PORT: int = int(os.getenv("RMQ_PORT", 5672))
    RABBITMQ_VHOST: str = os.getenv("RMQ_VHOST", "/")
    RABBITMQ_JOB_QUEUE_NAME: str = os.getenv("RMQ_JOB_QUEUE_NAME", "BBC_JOB_QUEUE")
    RABBITMQ_TASK_QUEUE_NAME: str = os.getenv("RMQ_TASK_QUEUE_NAME", "BBC_TASK_QUEUE")
    RABBITMQ_USER: str = os.getenv("RMQ_USER", "guest")
    RABBITMQ_PASSWORD: str = os.getenv("RMQ_PASSWORD", "guest")
    RABBITMQ_URL: str =  f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST_NAME}:{RABBITMQ_PORT}/"
    RETRIES: int = 5
    RETRY_BACKOFF_FACTOR: float = 2.0

@dataclass
class PostgresDBConfig:
    """
    Configuration for PostgreSQL database connection.

    Environment Variables
    ---------------------
    POSTGRES_DATABASE_NAME : str
        Name of the PostgreSQL database (default: 'BBC_NEWS_DATABASE').

    POSTGRES_TABLE_NAME : str
        Name of the table to store news articles (default: 'BBC_NEWS_TABLE').

    POSTGRES_HOST : str
        Host address of the PostgreSQL server (default: 'localhost').

    POSTGRES_PORT : int
        Port number for the PostgreSQL server (default: 5432).

    POSTGRES_USER : str
        Username for the PostgreSQL database (default: 'admin').

    POSTGRES_PASSWORD : str
        Password for the PostgreSQL database (default: 'admin').
    """
    POSTGRES_SERVICE_NAME: str = os.getenv("PGDB_SERVICE_NAME", "PostgresService")
    POSTGRES_DATABASE_NAME: str = os.getenv("PGDB_DATABASE_NAME", "BBC_NEWS_DATABASE")
    POSTGRES_TABLE_NAME: str = os.getenv("PGDB_TABLE_NAME", "BBC_NEWS_TABLE")
    POSTGRES_HOST_NAME: str = os.getenv("PGDB_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("PGDB_PORT", 5432))
    POSTGRES_USER: str = os.getenv("PGDB_USER", "admin")
    POSTGRES_PASSWORD: str = os.getenv("PGDB_PASSWORD", "admin")

# --- Components Configs ----

@dataclass
class BotConfig:
    """
    Configuration settings for the Selenium bot used in scraping.

    Attributes
    ----------
    HEADLESS : bool
        Whether to run the browser in headless mode.
    RETRY_ATTEMPTS : int
        Number of retry attempts for failed interactions.
    POPUP_TIMEOUT : int
        Timeout duration (in seconds) to wait for popups or modals.

    IFRAME_LOGIN_PAGE_SELECTOR : str
        Selector for the login iframe element.
    IFRAME_REGISTRATION_PAGE_SELECTOR : str
        Selector for the registration iframe element.
    CONTINUE_BUTTON_CLASS_SELECTOR : str
        CSS class name for the button used to close subscription popups.
    CLOSE_BUTTON_CLASS_SELECTOR : str
        CSS selector for the close button on article overlays.

    PAGINATION_SELECTOR : str
        CSS selector for the pagination component.
    LIVERPOOL_CARD_SELECTOR : str
        CSS selector for the Liverpool news card.

    LINK_ATTRIBUTE : str
        HTML attribute used to extract links (typically "href").
    ARTICLE_LINK_POSTFIXES : Tuple[str, ...]
        URL path postfixes used to filter relevant article links.

    Environment Variables
    ---------------------
    SELENIUM_HOST : str
        Hostname of the Selenium server (e.g., "localhost" or "selenium").
    SELENIUM_PORT : int
        Port number for the Selenium WebDriver server.

    SELENIUM_REMOTE_URL : str (property)
        Computed URL for connecting to the remote Selenium WebDriver server.
    """
    HEADLESS: bool = True
    RETRY_ATTEMPTS: int = 5
    POPUP_TIMEOUT: int = 10
    IFRAME_LOGIN_PAGE_SELECTOR: str = "offer_f096b6d430c8734495f0-0"
    IFRAME_REGISTRATION_PAGE_SELECTOR: str = "iframe[id^='offer-']"
    CONTINUE_BUTTON_CLASS_SELECTOR: str = "piano-bbc-close-button"
    CLOSE_BUTTON_CLASS_SELECTOR: str = "[class='pn-article__close']"
    PAGINATION_SELECTOR: str = "[data-testid='pagination']"
    LIVERPOOL_CARD_SELECTOR: str = "[data-testid='liverpool-card']"
    BASE_URL: str = "https://www.bbc.com/pages/content-index/{year:04d}/{month:02d}/{day:02d}?page={page_no}"
    ARTICLE_LINK_POSTFIXES: Tuple[str, ...] = (
        "/news/articles/",
        "/culture/articles/",
    )
    SELENIUM_SERVICE_NAME: str = os.getenv("SELENIUM_SERVICE_NAME", "SeleniumService")
    SELENIUM_HOST: str = os.getenv("SELENIUM_HOST", platform.node())
    SELENIUM_PORT: int = int(os.getenv("SELENIUM_PORT", 4444))
    SELENIUM_REMOTE_URL: str = f"http://{SELENIUM_HOST}:{SELENIUM_PORT}/wd/hub"
    MIN_HUMAN_DELAY: int = 1
    MAX_HUMAN_DELAY: int = 5

@dataclass
class UrlScraperConfig:
    """
    Configuration settings for the URL scraper.

    Attributes
    ----------
    URL_SCRAPER_HOST : str
        Hostname or identifier of the machine running the scraper.
        Defaults to the current machine's node name.
    AVERAGE_DAILY_ARTICLE_COUNT : int
        Estimated number of articles published per day. Used for planning scraping load.
    START_DATE : str
        Start date for scraping in 'YYYY-MM-DD' format.
    END_DATE : str
        End date for scraping in 'YYYY-MM-DD' format.
        By default, this is set to a fixed date. Can be set dynamically to today's date.

    Notes
    -----
    To dynamically set the end date to today's date, replace `END_DATE` with:
        datetime.now().strftime("%Y-%m-%d")
    """
    SERVICE_NAME: str = os.getenv("URL_SCRAPER_SERVICE_NAME", "UrlScraperSerivce")
    HOST_NAME: str = os.getenv("URL_SCRAPER_HOST", platform.node())
    ARCHIVED_DATA_LINK: str = "https://www.bbc.com/pages/content-index/{year:04d}/{month:02d}/{day:02d}?page={page_no}"

@dataclass
class DataETLConfig:
    SERVICE_NAME: str = os.getenv("CONSUMER_SERVICE_NAME", "ConsumerService")
    HOST_NAME: str = os.getenv("CONSUMER_HOST", platform.node())
    TASK_QUEUE_NAME: str = "BBC_TASK_QUEUE"
    MONGODB_DATA_COLLECTION_NAME: str = os.getenv("MONGODB_DATA_COLLECTION_NAME", "RAW_BBC_NEWS_COLLECTION")
    POSTGRES_TABLE_NAME: str = os.getenv("POSTGRES_TABLE_NAME", "BBC_NEWS_TABLE")

# --- Service Configs ---

@dataclass
class WorkGeneratorConfig:
    """
    Configuration settings for generating scraping and ingestion tasks for BBC News archives.

    This configuration defines parameters used by the `WorkGenerator`
    component to identify missing data, generate article URLs, and enqueue tasks
    in RabbitMQ for processing.

    Attributes
    ----------
    WORK_CHECKPOINT_COLLECTION_NAME : str
        Name of the MongoDB collection where scraper progress is stored.
        Used to track which dates have already been processed.
        Default is 'WORK_CHECKPOINT'.
    JOB_QUEUE_NAME : str
        Name of the RabbitMQ queue where scraping tasks are published.
        Default is 'BBC_JOB_QUEUE'.
    ARCHIVED_ARTICLES_START_DATE : str
        Earliest date to start scraping archived articles in 'YYYY-MM-DD' format.
        Default is '2017-06-01'.
    TODAYS_DATE : str
        Current system date in 'YYYY-MM-DD' format.
        Used to dynamically set the upper bound of scraping if not otherwise specified.

    Notes
    -----
    - `WORK_CHECKPOINT_COLLECTION_NAME` is used by `WorkGenerator` to check last_scrpaed_date date.
    - `JOB_QUEUE_NAME` is the queue name in RabbitMQ where url scrapping jobs are sent.
    """
    SERVICE_NAME: str = os.getenv("WG_SERVICE_NAME", "WorkGeneratorService")
    HOST_NAME: str = os.getenv("WG_HOST_NAME", platform.node())
    WORK_COLLECTION_NAME: str = "WORK_CHECKPOINT"
    JOB_QUEUE_NAME: str = "BBC_JOB_QUEUE"
    AVERAGE_DAILY_ARTICLE_COUNT: int = 50
    ARCHIVED_ARTICLES_START_DATE: str = "2017-06-01"
    TODAYS_DATE: str = datetime.now().strftime("%Y-%m-%d")

@dataclass
class ProducerConfig:
    SERVICE_NAME: str = os.getenv("PRODUCER_SERVICE_NAME", "ProducerService")
    HOST_NAME: str = os.getenv("PRODUCER_HOST_NAME", platform.node())
    FAILED_JOB_COLLECTION_NAME: str = "FAILED_JOB_COLLECTION"
    TASK_QUEUE_NAME: str = "BBC_TASK_QUEUE"

@dataclass
class ConsumerConfig:
    SERVICE_NAME: str = os.getenv("CONSUMER_SERVICE_NAME", "ConsumerService")
    HOST_NAME: str = os.getenv("CONSUMER_HOST_NAME", platform.node())
    TASK_QUEUE_NAME: str = "BBC_TASK_QUEUE"
    FAILED_TASK_COLLECTION_NAME: str = "FAILED_TASK_COLLECTION"
    DATA_COLLECTION_NAME: str = os.getenv("MDB_DATA_COLLECTION_NAME", "RAW_BBC_NEWS_COLLECTION")
    BACKUP_DATA_COLLECTION_NAME: str = os.getenv("MDB_BACKUP_DATA_COLLECTION_NAME", "BACKUP_BBC_NEWS_COLLECTION")
    DATA_TABLE_NAME: str = os.getenv("PGDB_TABLE_NAME", "BBC_NEWS_TABLE")
