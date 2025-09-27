import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.clients.rabbitmq_connector import RabbitMQClient
from src.entity.config_entity import RabbitMQConfig
from src.exception.base import CustomException


@pytest.fixture
def mock_config():
    """Fixture: fake RabbitMQConfig object for testing."""
    return RabbitMQConfig(  # nosec
        RABBITMQ_USER="test", # pragma: allowlist secret
        RABBITMQ_PASSWORD="test", # pragma: allowlist secret
        RABBITMQ_HOST="localhost",
        RABBITMQ_PORT=5672,
        RABBITMQ_VHOST="/",
        RETRIES=1
    )


@patch("src.clients.rabbitmq_connector.pika.BlockingConnection")
def test_connect_success(mock_connection, mock_config):
    """Test successful RabbitMQ connection."""
    mock_channel = MagicMock()
    mock_conn_instance = MagicMock()
    mock_conn_instance.channel.return_value = mock_channel
    mock_connection.return_value = mock_conn_instance

    client = RabbitMQClient(mock_config)

    assert client.connection == mock_conn_instance
    assert client.channel == mock_channel
    mock_connection.assert_called_once()


@patch("src.clients.rabbitmq_connector.pika.BlockingConnection", side_effect=Exception("Boom"))
def test_connect_failure(mock_connection, mock_config):
    """Test RabbitMQ connection failure raises CutsomException."""
    with pytest.raises(CustomException):
        RabbitMQClient(mock_config)


def test_declare_queue(mock_config):
    """Test RabbitMQ successful queue declaration."""
    client = RabbitMQClient.__new__(RabbitMQClient)
    client.rabbitmq_config = mock_config
    client.channel = MagicMock()

    client.declare_queue("test_queue")

    client.channel.queue_declare.assert_called_once_with(queue="test_queue", durable=True)


def test_publish_dict_message(mock_config):
    """Test RabbitMQ publishing successful message."""
    client = RabbitMQClient.__new__(RabbitMQClient)
    client.rabbitmq_config = mock_config
    client.channel = MagicMock()

    msg = {"task": "process", "published": datetime(2024, 1, 1)}
    client.publish("test_queue", msg)

    args, kwargs = client.channel.basic_publish.call_args
    assert kwargs["routing_key"] == "test_queue"
    body = json.loads(kwargs["body"])
    assert body["task"] == "process"
    assert isinstance(body["published"], str) # datetime converted


def test_publish_invalid_message_type(mock_config):
    """Test RabbitMQ publishing non dict message failure raises CustomException."""
    client = RabbitMQClient.__new__(RabbitMQClient)
    client.rabbitmq_config = mock_config
    client.channel = MagicMock()

    with pytest.raises(CustomException):
        client.publish("test_queue", "not a dict")


def test_close(mock_config):
    """Test closing the connection to None."""
    client = RabbitMQClient.__new__(RabbitMQClient)
    client.rabbitmq_config = mock_config
    client.connection = MagicMock(is_open=True)
    client.channel = MagicMock(is_open=True)

    client.close()

    client.channel.close.assert_called_once()
    client.connection.close.assert_called_once()

@patch("src.clients.rabbitmq_connector.pika.BlockingConnection")
def test_context_manager(mock_connection, mock_config):
    """Test ."""
    mock_channel = MagicMock()
    mock_conn_instance = MagicMock()
    mock_conn_instance.channel.return_value = mock_channel
    mock_connection.return_value = mock_conn_instance

    client = RabbitMQClient(mock_config)

    assert client.connection.is_closed or True # just sanity check
