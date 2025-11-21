import sys
import time
from typing import Dict, List, Optional, Tuple

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, PyMongoError

from src.entity.config_entity import MongoDBConfig
from src.exception.base import CustomException
from src.logger.logging_setup import JSONLogger, ensure_context_id, new_task_id


class MongoBaseRepository:
    """
    Base repository for handling core MongoDB operations with built-in logging,
    retry logic, and context management.

    This class serves as the foundation for higher-level database operations.
    It abstracts connection handling, collection retrieval, and CRUD operations
    with fault-tolerant retry mechanisms and structured JSON logging.

    Parameters
    ----------
    mongo_config : MongoDBConfig
        Configuration object containing MongoDB connection details such as URI,
        database name, and service metadata.
    job_id : str, optional
        Unique job identifier used for tracing operations in distributed pipelines.
    task_id : str, optional
        Unique identifier for an individual task within a job.
    context_id : str, optional
        Identifier for the current runtime context (useful in concurrent environments).
    parent_context_id : str, optional
        Identifier for a parent context if this operation is part of a hierarchical workflow.

    Notes
    -----
    - The class is designed to work with your structured logging (`JSONLogger`) and
      custom exception handler (`CustomException`).
    - All MongoDB operations include latency measurement and detailed execution tracing.
    - Intended for use within ETL or distributed scraping pipelines that require
      fault-tolerant database access.

    Examples
    --------
    >>> from src.entity.config_entity import MongoDBConfig
    >>> config = MongoDBConfig()
    >>> with MongoBaseRepository(config) as mongo_repo:
    ...     mongo_repo.insert_data("articles", [{"title": "Example"}])
    ...     results = mongo_repo.run_query("articles", {"title": "Example"})
    ...     print(results)
    """
    def __init__(
            self,
            mongo_config: MongoDBConfig,
            job_id: Optional[str] = None,
            task_id: Optional[str] = None,
            context_id: Optional[str] = None,
            parent_context_id: Optional[str] = None,
        ):
        """
        Initialize the MongoBaseRepository instance and establish a MongoDB client connection.

        Parameters
        ----------
        mongo_config : MongoDBConfig
            Configuration object with MongoDB URI, database name, and connection metadata.
        job_id : str, optional
            Unique identifier for the job.
        task_id : str, optional
            Unique identifier for the specific task.
        context_id : str, optional
            Identifier for the current execution context.
        parent_context_id : str, optional
            Identifier of the parent context for tracing nested operations.

        Raises
        ------
        CustomException
            If the connection to MongoDB cannot be established.
        """
        self.__mongo_config: MongoDBConfig = mongo_config
        self.__job_id: Optional[str] = job_id
        self.__task_id: Optional[str] = task_id
        self.__context_id: Optional[str] = context_id
        self.__parent_context_id: Optional[str] = parent_context_id
        self.logging = JSONLogger(
            service=self.__mongo_config.MONGODB_SERVICE_NAME,
            host=self.__mongo_config.MONGO_HOST,
            job_id=self.__job_id,
            task_id=self.__task_id,
            context_id=self.__context_id,
            parent_context_id=self.__parent_context_id,
        )
        self._client: Optional[MongoClient] = None

        self._connect()

    def get_context_id(self):
        return self.__context_id

    def get_parent_context_id(self):
        return self.__parent_context_id

    # +--------------------------+
    # | CHILD METHODS CAN ACCESS |
    # +--------------------------+
    @property
    def config(self):
        return self.__mongo_config

    # +---------------------+
    # | CONNECT TO MONGO DB |
    # +---------------------+
    @new_task_id
    @ensure_context_id
    def _connect(self):
        """
        Establish a MongoDB client connection with validation.

        This method initializes the MongoDB client and pings the database to ensure
        connectivity. It logs the connection status for debugging and monitoring.

        Raises
        ------
        CustomException
            If MongoDB is unreachable or the connection cannot be established.

        Examples
        --------
        >>> repo = MongoBaseRepository(config)
        >>> repo._connect()  # Typically invoked internally
        """
        start_time = time.perf_counter()
        try:
            self.logging.info("Establishing MongoDB client connection...", start_time)
            self._client = MongoClient(
                self.__mongo_config.MONGODB_URI,
                serverSelectionTimeoutMS=5000  # Fast fail if not reachable
            )
            # Test the connection
            self._client.admin.command("ping")
            self.logging.info("MongoDB connection established successfully.", start_time)
        except ConnectionFailure as e:
            self.logging.error(f"MongoDB connection failed: {e}", start_time)
            raise CustomException(f"Failed to connect to MongoDB: {e}", sys)

    # +----------------+
    # | GET COLLECTION |
    # +----------------+
    @new_task_id
    @ensure_context_id
    def _get_collection(self, collection_name: str) -> Collection:
        """
        Retrieve a MongoDB collection with retry and validation logic.

        The method ensures the client connection is active and attempts to fetch
        the requested collection. If it fails due to transient network or server
        issues, it retries based on the configured retry policy.

        Parameters
        ----------
        collection_name : str
            Name of the MongoDB collection to retrieve.

        Returns
        -------
        Collection
            The MongoDB collection object, ready for CRUD operations.

        Raises
        ------
        CustomException
            If the collection cannot be retrieved after all retry attempts.

        Examples
        --------
        >>> collection = repo._get_collection("articles")
        >>> print(collection.name)
        'articles'
        """
        start_time = time.perf_counter()

        for attempt in range(1, self.__mongo_config.MAX_RETRIES + 1):
            try:
                self.logging.info(f"[Attempt {attempt}] Getting collection: {collection_name}", start_time)

                if self._client is None:
                    self.logging.critical("MongoDB client is not initialized", start_time)
                    raise CustomException("MongoDB client is not initialized", sys)

                db = self._client[self.__mongo_config.MONGODB_DATABASE_NAME]
                collection = db[collection_name]

                # Ping the collection to validate access
                collection.estimated_document_count()

                self.logging.info("MongoDB collection retrieved successfully.", start_time)

                return collection
            except PyMongoError as e:
                self.logging.warning(f"Attempt {attempt} failed: {e}", start_time)
                if attempt < self.__mongo_config.MAX_RETRIES:
                    time.sleep(self.__mongo_config.RETRY_DELAY * (2 ** (attempt - 1)))
                else:
                    self.logging.error("Exceeded maximum retries for getting collection.", start_time)
                    raise CustomException(f"Failed to get MongoDB collection: {e}", sys)

    # +---------------+
    # | DISCONNECT DB |
    # +---------------+
    @new_task_id
    @ensure_context_id
    def _close_connection(self):
        """
        Gracefully close the MongoDB client connection.

        Ensures all resources are released and prevents stale client handles
        from persisting in long-running applications.

        Raises
        ------
        CustomException
            If closing the connection fails.

        Examples
        --------
        >>> repo.close_connection()
        >>> assert repo._client is None
        """
        start_time = time.perf_counter()
        try:
            if self._client:
                self.logging.info("Closing MongoDB client connection...", start_time)
                self._client.close()
                self.logging.info("MongoDB connection closed.", start_time)
        except Exception as e:
            self.logging.error(f"Error closing MongoDB connection: {e}", start_time)
            raise CustomException(e, sys)
        finally:
            self._client = None

    # +-------------------------+
    # | CONNECT CONTEXT MANAGER |
    # +-------------------------+
    def __enter__(self):
        """
        Enter runtime context for use with `with` statements.

        Returns
        -------
        MongoBaseRepository
            The current repository instance.

        Examples
        --------
        >>> with MongoBaseRepository(config) as repo:
        ...     repo.insert_data("news", [{"headline": "Example"}])
        """
        return self

    # +----------------------------+
    # | DISCONNECT CONTEXT MANAGER |
    # +----------------------------+
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit runtime context and close MongoDB connection.

        Parameters
        ----------
        exc_type : type, optional
            Exception type raised inside the context block.
        exc_val : Exception, optional
            Exception instance raised.
        exc_tb : traceback, optional
            Traceback object of the raised exception.
        """
        self._close_connection()

    @new_task_id
    @ensure_context_id
    def insert_data(self, collection_name: str, data: List[Dict]):
        """
        Insert multiple documents into a specified MongoDB collection.

        Parameters
        ----------
        collection_name : str
            Name of the collection where data will be inserted.
        data : list of dict
            A list of documents to insert into the collection.

        Raises
        ------
        CustomException
            If insertion fails due to database or connection errors.

        Examples
        --------
        >>> data = [
        ...     {"title": "Breaking News", "published": datetime(2023, 8, 25)},
        ...     {"title": "Tech Update", "published": datetime(2023, 8, 26)}
        ... ]
        >>> repo.insert_data("articles", data)
        """
        start_time = time.perf_counter()
        try:
            collection = self._get_collection(collection_name)
            self.logging.info(f"Inserting data to MongoDB collection {collection_name}", start_time)
            collection.insert_many(data)
        except Exception as e:
            self.logging.error(f"Error while inserting data to MongoDB: {e}", start_time)
            raise CustomException(e, sys)

    @new_task_id
    @ensure_context_id
    def run_query(
        self,
        collection_name:str,
        query: Optional[Dict] = None,
        projection: Optional[Dict] = None,
        limit: Optional[int] = None,
        sort: Optional[List[Tuple[str, int]]] = None,
    ) -> Optional[List[Dict]]:
        """
        Execute a MongoDB `find()` query with optional filters, projections, limits, and sorting.

        Parameters
        ----------
        collection_name : str
            Name of the MongoDB collection to query.
        query : dict, optional
            MongoDB filter query. Defaults to an empty filter (match all documents).
        projection : dict, optional
            Fields to include or exclude from the results, e.g., {"_id": 0, "title": 1}.
        limit : int, optional
            Maximum number of documents to return.
        sort : list of tuple, optional
            Sorting criteria, e.g., [("published", -1)] for descending order.

        Raises
        ------
        CustomException
            If the query execution fails.

        Examples
        --------
        >>> query = {"category": "technology"}
        >>> projection = {"_id": 0, "title": 1, "published": 1}
        >>> results = repo.run_query("articles", query=query, projection=projection, limit=5)
        >>> for doc in results:
        ...     print(doc["title"])
        """
        start_time = time.perf_counter()
        query = query or {}

        try:
            collection = self._get_collection(collection_name)
            self.logging.info(f"Running MongoDB query on '{collection.name}' | Query: {query}", start_time)

            cursor = collection.find(filter=query, projection=projection)

            if sort:
                cursor = cursor.sort(sort)
            if limit:
                cursor = cursor.limit(limit)

            results = list(cursor)
            if not results:
                self.logging.info(f"No documents found for query in collection '{collection.name}'.", start_time)
                return None

            self.logging.debug(f"Query returned {len(results)} documents from '{collection.name}'.", start_time)
            return results

        except PyMongoError as e:
            self.logging.error(f"MongoDB query failed: {e}", start_time)
            raise CustomException(e, sys)
