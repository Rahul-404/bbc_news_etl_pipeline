from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.clients.postgress_connector import PostgreSQLOperation
from src.entity.config_entity import PostgresDBConfig
from src.exception.base import CustomException


@pytest.fixture
def mock_config():
    """Fixture: mock Postgres config."""
    return PostgresDBConfig(    # nosec
        POSTGRES_DATABASE_NAME="test_db",
        POSTGRES_USER="user",
        POSTGRES_PASSWORD="pass", # pragma: allowlist secret
        POSTGRES_HOST="localhost",
        POSTGRES_PORT=5432,
        POSTGRES_TABLE_NAME="test_table",
    )


@pytest.fixture
def db_client(mock_config):
    return PostgreSQLOperation(mock_config)


@patch("src.clients.postgress_connector.psycopg2.connect")
def test_get_connection_success(mock_connect, db_client):
    """Should return connection when psycopg2.connect succeeds."""
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn

    conn = db_client.get_connection()

    assert conn == mock_conn
    mock_connect.assert_called_once_with(
        dbname=db_client.postgres_config.POSTGRES_DATABASE_NAME,
        user=db_client.postgres_config.POSTGRES_USER,
        password=db_client.postgres_config.POSTGRES_PASSWORD,
        host=db_client.postgres_config.POSTGRES_HOST,
        port=db_client.postgres_config.POSTGRES_PORT,
    )


@patch("src.clients.postgress_connector.psycopg2.connect", side_effect=Exception("DB down"))
def test_get_connection_failure(mock_connect, db_client):
    """Should raise after retries if connection fails."""
    with pytest.raises(Exception):  # Tenacity retries inside
        db_client.get_connection()

@patch("src.clients.postgress_connector.PostgreSQLOperation.get_connection")
def test_connection_cursor_commit(mock_conn_method, db_client):
    """Context manager should commit transaction on success."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn_method.return_value = mock_conn

    with db_client.connection_cursor() as (conn, cursor):
        cursor.execute("SELECT 1;")

    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("src.clients.postgress_connector.PostgreSQLOperation.get_connection")
def test_connection_cursor_rollback_on_exception(mock_conn_method, db_client):
    """Context manager should rollback if exception raised."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn_method.return_value = mock_conn

    with pytest.raises(RuntimeError):
        with db_client.connection_cursor() as (_, cursor):
            raise RuntimeError("fail!")

    mock_conn.rollback.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("src.clients.postgress_connector.PostgreSQLOperation.connection_cursor")
def test_table_exists_true(mock_cursor_ctx, db_client):
    """Should return True if table exists."""
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = [True]
    mock_cursor_ctx.return_value.__enter__.return_value = (None, mock_cursor)

    result = db_client.table_exists()
    assert result is True


@patch("src.clients.postgress_connector.PostgreSQLOperation.connection_cursor")
def test_table_exists_false(mock_cursor_ctx, db_client):
    """Should return False if table does not exist."""
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = [False]
    mock_cursor_ctx.return_value.__enter__.return_value = (None, mock_cursor)

    result = db_client.table_exists()
    assert result is False


@patch("src.clients.postgress_connector.PostgreSQLOperation.connection_cursor")
def test_insert_article_success(mock_cursor_ctx, db_client):
    """Should insert article with valid dict."""
    mock_cursor = MagicMock()
    mock_cursor_ctx.return_value.__enter__.return_value = (None, mock_cursor)

    article = {
        "title": "Test",
        "author": "Author",
        "source": "UnitTest",
        "published_date": "2024-01-01T00:00:00Z",
        "scraped_date": "2024-01-02T00:00:00Z",
        "summary": "Summary",
        "content": "Content",
        "url": "http://test.com",
        "category": "news",
    }
    db_client.insert_article(article)

    mock_cursor.execute.assert_called_once()
    args, kwargs = mock_cursor.execute.call_args
    assert "INSERT INTO" in str(args[0])


@patch("src.clients.postgress_connector.PostgreSQLOperation.connection_cursor")
def test_insert_article_failure(mock_cursor_ctx, db_client):
    """Should raise CustomException if insert fails."""
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = Exception("Article insert failed")
    mock_cursor_ctx.return_value.__enter__.return_value = (None, mock_cursor)

    with pytest.raises(CustomException):
        db_client.insert_article({"url": "broken"})


@pytest.mark.parametrize(
    "date_str,expected",
    [
        ("2024-01-01T00:00:00Z", datetime(2024, 1, 1, 0, 0, 0, tzinfo=None)),
        ("", None),
        (None, None),
        ("invalid", None),
    ],
)
def test_parse_date_variants(db_client, date_str, expected):
    """_parse_date should handle ISO, empty, None, invalid."""
    result = db_client._parse_date(date_str)
    if expected:
        assert isinstance(result, datetime)
    else:
        assert result is None


@patch("src.clients.postgress_connector.PostgreSQLOperation.connection_cursor")
def test_create_table(mock_cursor_ctx, db_client):
    """Should execute create table query."""
    mock_cursor = MagicMock()
    mock_cursor_ctx.return_value.__enter__.return_value = (None, mock_cursor)

    db_client.create_table()
    mock_cursor.execute.assert_called_once()
    assert "CREATE TABLE" in str(mock_cursor.execute.call_args[0][0])
