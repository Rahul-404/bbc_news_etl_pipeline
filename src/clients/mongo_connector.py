import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, PyMongoError

from src.entity.config_entity import MongoDBConfig
from src.exception.base import CustomException
from src.logger.logging_setup import get_logger

logging = get_logger("MongoService")

class MongoDBOperation:
    """
    Handles MongoDB operations such as connecting to a collection,
    inserting documents, checking for existing records, and retrieving
    documents grouped by date.

    Parameters
    ----------
    mongo_db_config : MongoDBConfig
        Configuration object containing MongoDB connection details.
    max_retries : int, default=3
        Maximum number of retries to get a MongoDB collection.
    retry_delay : float, default=1.0
        Initial delay between retries in seconds. Doubles each attempt.

    Examples
    --------
    >>> from src.entity.config_entity import MongoDBConfig
    >>> from src.clients.mongo_connector import MongoDBOperation
    >>> config = MongoDBConfig()
    >>> with MongoDBOperation(config) as mongo_op:
    ...     mongo_op.insert_data([{"title": "Example", "published": datetime.utcnow()}])
    ...     exists = mongo_op.is_article_link_exists("http://example.com/article")
    ...     print("Article exists:", exists)
    """

    def __init__(self, mongo_db_config: MongoDBConfig, max_retries: int = 3, retry_delay: float = 1.0):
        """
        Initialize MongoDBOperation with config and establish MongoDB client connection.

        Parameters
        ----------
        mongo_db_config : MongoDBConfig
            Configuration object with MongoDB settings.
        max_retries : int, default=3
            Maximum retry attempts for collection retrieval.
        retry_delay : float, default=1.0
            Initial delay between retries (seconds).

        Raises
        ------
        CustomException
            If connection fails.
        """
        self.mongo_db_config = mongo_db_config
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.client: Optional[MongoClient] = None
        self._collection = None

        self._connect()


    def _connect(self):
        """
        Establish a MongoDB client connection.

        Raises
        ------
        CustomException
            If connection to MongoDB fails.
        """
        try:
            logging.info("Establishing MongoDB client connection...")
            self.client = MongoClient(
                self.mongo_db_config.MONGODB_URI,
                serverSelectionTimeoutMS=5000  # Fast fail if not reachable
            )
            # Test the connection
            self.client.admin.command("ping")
            logging.info("MongoDB connection established successfully.")
        except ConnectionFailure as e:
            logging.error(f"MongoDB connection failed: {e}")
            raise CustomException("Failed to connect to MongoDB", sys)


    def _get_collection(self) -> Collection:
        """
        Retrieve the MongoDB collection with retry logic.

        Returns
        -------
        Collection
            The MongoDB collection object.

        Raises
        ------
        CustomException
            If retrieval fails after retries.
        """
        if self._collection:
            return self._collection

        for attempt in range(1, self.max_retries + 1):
            try:
                logging.info(f"[Attempt {attempt}] Getting collection: "
                             f"{self.mongo_db_config.MONGODB_COLLECTION_NAME}")

                if self.client is None:
                    raise CustomException("MongoDB client is not initialized", sys)

                db = self.client[self.mongo_db_config.MONGODB_DATABASE_NAME]
                collection = db[self.mongo_db_config.MONGODB_COLLECTION_NAME]

                # Ping the collection to validate access
                collection.estimated_document_count()
                logging.info("MongoDB collection retrieved successfully.")
                self._collection = collection
                return collection
            except PyMongoError as e:
                logging.warning(f"Attempt {attempt} failed: {e}")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * (2 ** (attempt - 1)))
                else:
                    logging.error("Exceeded maximum retries for getting collection.")
                    raise CustomException("Failed to get MongoDB collection", sys)


    @property
    def collection(self) -> Collection:
        """
        MongoDB collection instance (lazy-loaded with retry).

        Returns
        -------
        Collection
            MongoDB collection object.
        """
        return self._get_collection()


    def get_date_wise_doc_count(self) -> Optional[List[Tuple[datetime, int]]]:
        """
        Get the dates and respective document counts, ordered by date.

        Returns
        -------
        list of tuple of (datetime.date, int) or None
            List of tuples containing (date, document count).
            Returns None if no documents are found.

        Raises
        ------
        CustomException
            If query execution fails.

        Examples
        --------
        >>> counts = mongo_op.get_date_wise_doc_count()
        >>> if counts:
        ...     for date, count in counts:
        ...         print(date, count)
        """
        try:
            pipeline = [
                            {
                                "$group": {
                                    "_id": {  # Extract just the date part (Y-M-D)
                                        "$dateToString": {
                                            "format": "%Y-%m-%d",
                                            "date": "$published"
                                        }
                                    },
                                    "documents": { "$push": "$$ROOT" },  # Group all documents for the same date
                                    "count": { "$sum": 1 }  # Optional: count of documents per date
                                }
                            },
                            {
                                "$sort": { "_id": 1 }  # Sort by date ascending
                            }
                        ]
            result = list(self.collection.aggregate(pipeline))
            date_wise_count = None
            if result:
                # Convert _id from string to datetime.date
                date_wise_count = [
                    (group['_id'], group['count'])
                    for group in result
                ]
                logging.debug(f"Fetched latest document: {date_wise_count}")
                return date_wise_count
            else:
                logging.info(f"No documents found : {date_wise_count}.")
                return date_wise_count
        except Exception as e:
            logging.error(f"Error fetching latest date: {e}")
            raise CustomException(e, sys)


    def insert_data(self, data: List[Dict]):
        """
        Insert multiple documents into the MongoDB collection.

        Parameters
        ----------
        data : list of dict
            Documents to insert.

        Raises
        ------
        CustomException
            If insertion fails.

        Examples
        --------
        >>> documents = [
        ...     {"title": "Breaking News", "published": datetime(2023, 8, 25)},
        ...     {"title": "Tech Update", "published": datetime(2023, 8, 26)}
        ... ]
        >>> mongo_op.insert_data(documents)
        """
        try:
            logging.info(f"Inserting data to MongoDB collection {self.mongo_db_config.MONGODB_COLLECTION_NAME}")
            self.collection.insert_many(data)
        except Exception as e:
            logging.error(f"Error while inserting data to MongoDB: {e}")
            raise CustomException(e, sys)


    def is_article_link_exists(self, article_link: str):
        """
        Check if a document with the given article link exists.

        Parameters
        ----------
        article_link : str
            URL of the article.

        Returns
        -------
        bool
            True if the document exists, False otherwise.

        Raises
        ------
        CustomException
            If query fails.

        Examples
        --------
        >>> exists = mongo_op.is_article_link_exists("http://example.com/article123")
        >>> print(exists)
        True
        """
        try:
            doc_url = self.collection.find_one(
                filter={
                    self.mongo_db_config.MONGO_DOC_ARTICLE_URL_KEY: article_link,
                }
            )

            if doc_url is not None:
                logging.info(f"Document exists for Url: {article_link}")
                return True
            else:
                logging.info(f"No document exists for Url: {article_link}")
                return False
        except Exception as e:
            logging.error(f"Error while fetching data from MongoDB: {e}")
            raise CustomException(e, sys)


    def close_connection(self):
        """
        Gracefully close the MongoDB client connection.

        Raises
        ------
        CustomException
            If closing the connection fails.

        Examples
        --------
        >>> mongo_op.close_connection()
        """
        try:
            if self.client:
                logging.info("Closing MongoDB client connection...")
                self.client.close()
                self.client = None
                self._collection = None
                logging.info("MongoDB connection closed.")
        except Exception as e:
            logging.error(f"Error closing MongoDB connection: {e}")
            raise CustomException(e, sys)

    def __enter__(self):
        """
        Enter runtime context (for `with` statement).

        Returns
        -------
        MongoDBOperation
            The MongoDBOperation instance.

        Examples
        --------
        >>> with MongoDBOperation(config) as mongo_op:
        ...     mongo_op.insert_data([{"title": "inside context"}])
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit runtime context and close MongoDB connection.

        Parameters
        ----------
        exc_type : type
            Exception type (if raised inside context).
        exc_val : Exception
            Exception instance (if raised).
        exc_tb : traceback
            Traceback object.
        """
        self.close_connection()
