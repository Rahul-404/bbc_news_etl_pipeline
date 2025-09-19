from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from pymongo.errors import ConnectionFailure

from src.clients.mongo_connector import MongoDBOperation
from src.entity.config_entity import MongoDBConfig
from src.exception.base import CustomException


@pytest.fixture
def mongo_config():
    """Fixture: fake MongoDBConfig object for testing."""
    return MongoDBConfig(
        MONGODB_URI="mongodb://localhost:27017",
        MONGODB_DATABASE_NAME="test_db",
        MONGODB_COLLECTION_NAME="test_collection",
        MONGO_DOC_ARTICLE_URL_KEY="url"
    )


@patch("src.clients.mongo_connector.MongoClient")
def test_connect_success(mock_mongo, mongo_config):
    """Test successful MongoDB connection."""
    mock_client = MagicMock()
    mock_mongo.return_value = mock_client
    mock_client.admin.command.return_value = {"ok": 1}

    mongo_op = MongoDBOperation(mongo_config)
    assert mongo_op.client == mock_client # nosec B101


@patch("src.clients.mongo_connector.MongoClient")
def test_connect_failure(mock_mongo, mongo_config):
    """Test MongoDB connection failure raises CustomException."""
    mock_client = MagicMock()
    mock_mongo.return_value = mock_client

    # Simulate a failure during ping (as MongoClient would throw in real case)
    mock_client.admin.command.side_effect = ConnectionFailure("Ping Failed")

    # Now we expect that MongoDBOperation will catch the above and raise CustomException
    with pytest.raises(CustomException) as exc_info:
        MongoDBOperation(mongo_config)

    # Assert that your error message is included in the custom exception
    assert "Failed to connect to MongoDB" in str(exc_info.value) # nosec B101


@patch("src.clients.mongo_connector.MongoClient")
def test_insert_data(mock_mongo, mongo_config):
    """Test insert_data calls insert_many."""
    mock_collection = MagicMock()
    mock_client = MagicMock()
    mock_client.__getitem__.return_value = {mongo_config.MONGODB_COLLECTION_NAME: mock_collection}
    mock_mongo.return_value = mock_client
    mock_client.admin.command.return_value = {"ok": 1}

    mongo_op = MongoDBOperation(mongo_config)
    mongo_op._collection = mock_collection

    data = [{"title": "Test", "published": datetime.utcnow()}]
    mongo_op.insert_data(data)

    mock_collection.insert_many.assert_called_once_with(data) # nosec B101


@patch("src.clients.mongo_connector.MongoClient")
def test_is_article_link_exists_true(mock_mongo, mongo_config):
    """Test is_article_link_exists returns True when doc exists."""
    mock_collection = MagicMock()
    mock_collection.find_one.return_value = {"url": "http://example.com"}
    mock_client = MagicMock()
    mock_mongo.return_value = mock_client
    mock_client.__getitem__.return_value = {mongo_config.MONGODB_COLLECTION_NAME: mock_collection}
    mock_client.admin.command.return_value = {"ok": 1}

    mongo_op = MongoDBOperation(mongo_config)
    mongo_op._collection = mock_collection

    result = mongo_op.is_article_link_exists("http://example.com")

    assert result is True # nosec B101


@patch("src.clients.mongo_connector.MongoClient")
def test_is_article_link_exists_false(mock_mongo, mongo_config):
    """Test is_article_link_exists return False when no doc found."""
    mock_collection = MagicMock()
    mock_collection.find_one.return_value = None
    mock_client = MagicMock()
    mock_mongo.return_value = mock_client
    mock_client.__getitem__.return_value = {mongo_config.MONGODB_COLLECTION_NAME: mock_collection}
    mock_client.admin.command.return_valie = {"ok": 1}

    mongo_op = MongoDBOperation(mongo_config)
    mongo_op._collection = mock_collection

    result = mongo_op.is_article_link_exists("http://nonexistent.com")

    assert result is False # nosec B101


@patch("src.clients.mongo_connector.MongoClient")
def test_get_date_wise_doc_count(mock_mongo, mongo_config):
    """Test aggregation pipeline for date-wise doc count."""
    mock_collection = MagicMock()
    mock_collection.aggregate.return_value = [
        {"_id": "2023-08-25", "count": 2},
        {"_id": "2023-08-26", "count": 1}
    ]
    mock_client = MagicMock()
    mock_mongo.return_value = mock_client
    mock_client.__getitem__.return_value = {mongo_config.MONGODB_COLLECTION_NAME: mock_collection}
    mock_client.admin.command.return_value = {"ok": 1}

    mongo_op = MongoDBOperation(mongo_config)
    mongo_op._collection = mock_collection

    result = mongo_op.get_date_wise_doc_count()

    expected = [
        ("2023-08-25", 2),
        ("2023-08-26", 1)
    ]

    assert result == expected # nosec B101


@patch("src.clients.mongo_connector.MongoClient")
def test_close_connection(mock_mongo, mongo_config):
    """Test close_conneciton sets client and collection to None."""
    mock_client = MagicMock()
    mock_mongo.return_value = mock_client
    mock_client.admin.command.return_value = {"ok": 1}

    mongo_op = MongoDBOperation(mongo_config)
    mongo_op.close_connection()

    assert mongo_op.client is None # nosec B101
    assert mongo_op._collection is None # nosec B101
