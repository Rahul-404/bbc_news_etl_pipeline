import os
from dataclasses import dataclass

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
