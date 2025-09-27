import time
from contextlib import contextmanager
from datetime import datetime
from typing import Dict

import psycopg2
from psycopg2 import sql
from tenacity import retry, stop_after_attempt, wait_fixed

from src.entity.config_entity import PostgresDBConfig
from src.exception.base import CustomException
from src.logger.logging_setup import get_logger
from src.utils import calculate_duration

service_name = "PostgresService"

logger = get_logger(service_name)

class PostgreSQLOperation:
    """
    PostgreSQLOperation handles PostgreSQL database operations safely with retries, context-managed cursors,
    table creation, and CRUD operations with proper logging.

    Attributes
    ----------
    postgres_config : PostgresDBConfig
        Configuration object containing PostgreSQL connection details.

    Examples
    --------
    >>> from src.entity.config_entity import PostgresDBConfig
    >>> config = PostgresDBConfig()
    >>> db_client = PostgreSQLOperation(config)
    >>> db_client.create_table()
    >>> article = {
    ...     "title": "Sample Article",
    ...     "author": "John Doe",
    ...     "source": "BBC",
    ...     "published_date": "2025-09-27T10:00:00Z",
    ...     "scraped_date": "2025-09-27T11:00:00Z",
    ...     "summary": "This is a summary",
    ...     "content": "Full content here",
    ...     "url": "https://example.com/article1",
    ...     "category": "News"
    ... }
    >>> db_client.insert_article(article)
    >>> db_client.table_exists()
    True
    """
    def __init__(self, postgres_config: PostgresDBConfig):
        """
        Initialize PostgreSQLOperation with configuration.

        Parameters
        ----------
        postgres_config : PostgresDBConfig
            Contains all necessary DB connection info like host, port, user, password, and table name.
        """
        self.postgres_config = postgres_config

    @retry(wait=wait_fixed(2), stop=stop_after_attempt(5))
    def get_connection(self):
        """
        Establish a connection to PostgreSQL with retry logic.

        Returns
        -------
        connection : psycopg2.extensions.connection
            Active connection object.

        Raises
        ------
        psycopg2.OperationalError
            If connection cannot be established after retries.

        Examples
        --------
        >>> conn = db_client.get_connection()
        >>> conn.closed
        0
        """
        return psycopg2.connect(
            dbname=self.postgres_config.POSTGRES_DATABASE_NAME,
            user=self.postgres_config.POSTGRES_USER,
            password=self.postgres_config.POSTGRES_PASSWORD,
            host=self.postgres_config.POSTGRES_HOST,
            port=self.postgres_config.POSTGRES_PORT
        )

    @contextmanager
    def connection_cursor(self):
        """
        Context manager for PostgreSQL connection and cursor.

        Ensures commit on success and rollback on failure.

        Yields
        ------
        conn : psycopg2.extensions.connection
        cursor : psycopg2.extensions.cursor

        Raises
        ------
        Exception
            Any exception during DB operation is propagated after rollback.

        Examples
        --------
        >>> with db_client.connection_cursor() as (conn, cursor):
        ...     cursor.execute("SELECT 1;")
        ...     cursor.fetchone()
        (1,)
        """
        start_time = time.perf_counter()
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield conn, cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(
                "Database operation failed",
                extra={
                    "service": service_name,
                    "host": self.postgres_config.POSTGRES_HOST,
                    "stack_trace": str(e),
                    "duration_ms": calculate_duration(start_time),
                }
            )
            raise
        finally:
            cursor.close()
            conn.close()

    def table_exists(self) -> bool:
        """
        Check if the target table exists in the 'public' schema.

        Returns
        -------
        exists : bool
            True if table exists, False otherwise.

        Raises
        ------
        CustomException
            If the check fails due to a DB error.

        Examples
        --------
        >>> db_client.table_exists()
        True
        """
        check_query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = %s
        );
        """
        start_time = time.perf_counter()
        with self.connection_cursor() as (_, cursor):
            try:
                cursor.execute(check_query, (self.postgres_config.POSTGRES_TABLE_NAME,))
                exists = cursor.fetchone()[0]
                logger.info(
                    f"Table '{self.postgres_config.POSTGRES_TABLE_NAME}' exists: {exists}",
                    extra={
                        "service": service_name,
                        "host": self.postgres_config.POSTGRES_HOST,
                        "duration_ms": calculate_duration(start_time),
                    }
                )
                return exists
            except Exception as e:
                logger.error(
                    "Failed to check if table exists",
                    extra={
                        "service": service_name,
                        "host": self.postgres_config.POSTGRES_HOST,
                        "stack_trace": str(e),
                        "duration_ms": calculate_duration(start_time),
                    }
                )
                raise CustomException("Table existence check failed", e)

    def create_table(self):
        """
        Create the main articles table if it does not exist.

        Table structure:
        - id : SERIAL PRIMARY KEY
        - title : TEXT NOT NULL
        - author : TEXT
        - source : TEXT
        - publish_date : TIMESTAMP
        - scraped_date : TIMESTAMP
        - summary : TEXT
        - content : TEXT
        - url : TEXT UNIQUE NOT NULL
        - category : TEXT
        - created_at : TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        Raises
        ------
        psycopg2.Error
            If table creation fails.

        Examples
        --------
        >>> db_client.create_table()
        Table 'articles' ensured to exist.
        """

        start_time = time.perf_counter()
        create_table_query = sql.SQL("""
        CREATE TABLE IF NOT EXISTS {table} (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT,
            source TEXT,
            publish_date TIMESTAMP,
            scraped_date TIMESTAMP,
            summary TEXT,
            content TEXT,
            url TEXT UNIQUE NOT NULL,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """).format(
                table=sql.Identifier(self.postgres_config.POSTGRES_TABLE_NAME)
            )
        with self.connection_cursor() as (_, cursor):
            cursor.execute(create_table_query)
            logger.info(
                f"Table {self.postgres_config.POSTGRES_TABLE_NAME} ensured to exist.",
                extra={
                        "service": service_name,
                        "host": self.postgres_config.POSTGRES_HOST,
                        "duration_ms": calculate_duration(start_time),
                    }
                )

    def insert_article(self, article_data: Dict):
        """
        Insert an article into the database.

        Uses `ON CONFLICT (url) DO NOTHING` to avoid duplicates.

        Parameters
        ----------
        article_data : dict
            Dictionary containing keys:
            'title', 'author', 'source', 'published_date', 'scraped_date',
            'summary', 'content', 'url', 'category'

        Raises
        ------
        CustomException
            If insertion fails.

        Examples
        --------
        >>> article = {
        ...     "title": "Test",
        ...     "author": "Alice",
        ...     "source": "BBC",
        ...     "published_date": "2025-09-27T10:00:00Z",
        ...     "scraped_date": "2025-09-27T11:00:00Z",
        ...     "summary": "Test summary",
        ...     "content": "Full content",
        ...     "url": "https://example.com/test",
        ...     "category": "News"
        ... }
        >>> db_client.insert_article(article)
        Article inserted: https://example.com/test
        """

        start_time = time.perf_counter()
        insert_query = sql.SQL("""
        INSERT INTO {table}
        (title, author, source, publish_date, scraped_date, summary, content, url, category)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (url) DO NOTHING
        """).format(
                table=sql.Identifier(self.postgres_config.POSTGRES_TABLE_NAME)
            )
        try:
            values = (
                article_data.get("title"),
                article_data.get("author"),
                article_data.get("source"),
                self._parse_date(article_data.get("published_date")),
                self._parse_date(article_data.get("scraped_date")),
                article_data.get("summary"),
                article_data.get("content"),
                article_data.get("url"),
                article_data.get("category"),
            )
            with self.connection_cursor() as (_, cursor):
                cursor.execute(insert_query, values)
                logger.info(
                    f"Article inserted: {article_data.get('url')}",
                    extra={
                        "service": service_name,
                        "host": self.postgres_config.POSTGRES_HOST,
                        "duration_ms": calculate_duration(start_time),
                    }
                )
        except Exception as e:
            logger.error(
                "Failed to insert article",
                extra={
                    "service": service_name,
                    "host": self.postgres_config.POSTGRES_HOST,
                    "stack_trace": str(e),
                    "duration_ms": calculate_duration(start_time),
                }
            )
            raise CustomException("Article insert failed", e)

    def _parse_date(self, date_str):
        """
        Parse ISO 8601 datetime string to Python datetime object.

        Parameters
        ----------
        date_str : str
            Datetime string, e.g. '2025-09-27T10:00:00Z'

        Returns
        -------
        datetime or None
            Parsed datetime object or None if invalid or empty.

        Examples
        --------
        >>> db_client._parse_date("2025-09-27T10:00:00Z")
        datetime.datetime(2025, 9, 27, 10, 0, tzinfo=datetime.timezone.utc)
        >>> db_client._parse_date(None)
        None
        """

        start_time = time.perf_counter()
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except ValueError as e:
            logger.warning(
                "Invalid datetime format",
                extra={
                    "service": service_name,
                    "host": self.postgres_config.POSTGRES_HOST,
                    "stack_trace": str(e),
                    "duration_ms": calculate_duration(start_time),
                }
            )
            return None

    def create_test_table(self):
        start_time = time.perf_counter()
        create_table_query = ("""
        CREATE TABLE IF NOT EXISTS {table} (
            id SERIAL PRIMARY KEY,
            url TEXT UNIQUE NOT NULL,
        );
        """).format(
            table = sql.Identifier(self.postgres_config.POSTGRES_TABLE_NAME)
        )
        with self.connection_cursor() as (_, cursor):
            cursor.execute(create_table_query)
            logger.info(
                f"Table {self.postgres_config.POSTGRES_TABLE_NAME} ensured to exist.",
                extra={
                        "service": service_name,
                        "host": self.postgres_config.POSTGRES_HOST,
                        "duration_ms": calculate_duration(start_time),
                }
            )


    def insert_test_article(self, article_data: Dict):
        start_time = time.perf_counter()
        insert_query = sql.SQL("""
        INSERT INTO {table}
        (id, url)
        VALUES (%s, %s)
        ON CONFLICT (url) DO NOTHING
        """).format(
            table=sql.Identifier(self.postgres_config.POSTGRES_TABLE_NAME)
            )
        try:
            values = (
                article_data.get("task_id"),
                article_data.get("url"),
            )
            with self.connection_cursor() as (_, cursor):
                cursor.execute(insert_query, values)
                logger.info(
                    f"Article inserted: {article_data.get('url')}",
                    extra={
                        "service": service_name,
                        "host": self.postgres_config.POSTGRES_HOST,
                        "duration_ms": calculate_duration(start_time),
                }
            )
        except Exception as e:
            logger.error(
                "Failed to insert article",
                extra={
                    "service": service_name,
                    "host": self.postgres_config.POSTGRES_HOST,
                    "stack_trace": str(e),
                    "duration_ms": calculate_duration(start_time),
                }
            )
            raise CustomException("Article insert failed", e)
