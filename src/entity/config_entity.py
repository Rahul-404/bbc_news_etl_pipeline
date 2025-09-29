import os
from dataclasses import dataclass
from typing import Tuple

from dotenv import load_dotenv

load_dotenv()

@dataclass
class MongoDBConfig:
    """
    Configuration for MongoDB connection and document schema.

    Environment Variables
    ---------------------
    MONGODB_DATABASE_NAME : str
        Name of the MongoDB database (default: 'BBC_NEWS_DATABASE').

    MONGODB_COLLECTION_NAME : str
        Name of the MongoDB collection (default: 'RAW_BBC_NEWS_COLLECTION').

    Attributes
    ----------
    MONGODB_DATABASE_NAME : str
        MongoDB database name.

    MONGODB_COLLECTION_NAME : str
        MongoDB collection name.

    MONGO_DOC_DATE_KEY : str
        Key name for the document's published date (default: 'published').

    MONGO_DOC_CATEGORY_KEY : str
        Key name for the document's category field (default: 'category').

    MONGO_DOC_SUB_CATEGORY_KEY : str
        Key name for the document's sub-category field (default: 'sub_category').

    MONGO_DOC_ARTICLE_URL_KEY : str
        Key name for the document's article URL (default: 'url').
    """
    MONGODB_DATABASE_NAME: str = os.getenv("MONGODB_DATABASE_NAME", "BBC_NEWS_DATABASE")
    MONGODB_COLLECTION_NAME: str = os.getenv("MONGODB_COLLECTION_NAME", "RAW_BBC_NEWS_COLLECTION")
    MONGO_DOC_DATE_KEY: str = "published"
    MONGO_DOC_CATEGORY_KEY: str = "category"          # Fixed typo here
    MONGO_DOC_SUB_CATEGORY_KEY: str = "sub_category"  # Fixed typo here
    MONGO_DOC_ARTICLE_URL_KEY: str = "url"
    MONGO_HOST: str = os.getenv("MONGO_HOST", "localhost")
    MONGO_PORT: int = int(os.getenv("MONGO_PORT", 27017))
    MONGODB_URI: str = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"

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
    RABBITMQ_HOST: str = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT: int = int(os.getenv("RABBITMQ_PORT", 5672))
    RABBITMQ_VHOST: str = os.getenv("RABBITMQ_VHOST", "/")
    RABBITMQ_QUEUE_NAME: str = os.getenv("RABBITMQ_QUEUE_NAME", "bbc_news_tasks")
    RABBITMQ_USER: str = os.getenv("RABBITMQ_USER", "guest")
    RABBITMQ_PASSWORD: str = os.getenv("RABBITMQ_PASSWORD", "guest")
    RABBITMQ_URL: str =  f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/"
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
    POSTGRES_DATABASE_NAME: str = os.getenv("POSTGRES_DATABASE_NAME", "BBC_NEWS_DATABASE")
    POSTGRES_TABLE_NAME: str = os.getenv("POSTGRES_TABLE_NAME", "BBC_NEWS_TABLE")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", 5432))
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "admin")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "admin")


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
    SELENIUM_HOST: str = os.getenv("SELENIUM_HOST", "selenium")
    SELENIUM_PORT: int = int(os.getenv("SELENIUM_PORT", 4444))
    SELENIUM_REMOTE_URL: str = f"http://{SELENIUM_HOST}:{SELENIUM_PORT}/wd/hub"
    MIN_HUMAN_DELAY: int = 1
    MAX_HUMAN_DELAY: int = 5
