import json
import random
import sys
import time
from datetime import datetime
from typing import Callable, Optional

import pika
from pika.exceptions import AMQPConnectionError, ChannelClosedByBroker

from src.entity.config_entity import RabbitMQConfig
from src.exception.base import CustomException
from src.logger.logging_setup import get_logger
from src.utils import calculate_duration

service_name = "RabbitMQService"

logging = get_logger(service_name)

class RabbitMQClient:
    """
    Client for interacting with a RabbitMQ message broker.

    Handles connection setup, publishing messages, queue declaration,
    and graceful shutdown with retry logic and error handling.

    Examples
    --------
    Basic usage:

    >>> from src.entity.config_entity import RabbitMQConfig
    >>> from src.clients.rabbitmq_connector import RabbitMQClient
    >>> config = RabbitMQConfig()
    >>> client = RabbitMQClient(config)
    >>> client.declare_queue('my_queue')
    >>> client.publish('my_queue', {"message": "Hello, world!"})
    >>> client.close()

    Context manager usage:

    >>> with RabbitMQClient(config) as client:
    ...     client.declare_queue('my_queue')
    ...     client.publish('my_queue', {"message": "Hello, with context manager!"})
    """

    def __init__(self, rabbitmq_config: RabbitMQConfig):
        """
        Initialize RabbitMQ client and establish a connection.

        The connection and channel are created with retry logic.

        Parameters
        ----------
        rabbitmq_config : RabbitMQConfig
            Configuration object with connection parameters.

        Examples
        --------
        >>> client = RabbitMQClient(config)
        >>> assert client.connection.is_open
        """
        self.rabbitmq_config = rabbitmq_config
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.adapters.blocking_connection.BlockingChannel] = None
        self._connect()


    def _connect(self):
        """
        Establish a connection to RabbitMQ with retries and exponential backoff.

        Retries using configuration parameters. Logs connection attempts
        and raises a `CustomException` on failure.

        Raises
        ------
        CustomException
            If unable to connect after all retry attempts or unexpected errors occur.
        """
        start_time = time.perf_counter()
        try:
            attempt = 0
            while attempt < self.rabbitmq_config.RETRIES:
                try:
                    credentials = pika.PlainCredentials(
                        username=self.rabbitmq_config.RABBITMQ_USER,
                        password=self.rabbitmq_config.RABBITMQ_PASSWORD
                    )

                    parameters = pika.ConnectionParameters(
                        host=self.rabbitmq_config.RABBITMQ_HOST,
                        port=self.rabbitmq_config.RABBITMQ_PORT,
                        virtual_host=self.rabbitmq_config.RABBITMQ_VHOST,
                        credentials=credentials,
                        heartbeat=600,
                        blocked_connection_timeout=300,
                    )

                    self.connection = pika.BlockingConnection(parameters)
                    self.channel = self.connection.channel()
                    logging.info(
                        "Connected to RabbitMQ successfully.",
                        extra={
                            "service": service_name,
                            "host": self.rabbitmq_config.RABBITMQ_HOST,
                            "duration_ms": calculate_duration(start_time),
                        }
                    )
                    break

                except AMQPConnectionError as e:
                    attempt += 1
                    logging.warning(
                        f"RabbitMQ connection attempt {attempt} failed",
                        extra={
                            "service": service_name,
                            "host": self.rabbitmq_config.RABBITMQ_HOST,
                            "stack_trace": str(e),
                            "duration_ms": calculate_duration(start_time),
                        }
                    )
                    time.sleep((self.rabbitmq_config.RETRY_BACKOFF_FACTOR ** attempt)  + random.uniform(0, 0.5))  # exponential backoff # nosec B311

                except Exception as e:
                    logging.error(
                        "Unexpected error connecting to RabbitMQ",
                        extra={
                            "service": service_name,
                            "host": self.rabbitmq_config.RABBITMQ_HOST,
                            "stack_trace": str(e),
                            "duration_ms": calculate_duration(start_time),
                        }
                    )
                    raise

            else:
                self.close()
                logging.error(
                        f"Failed to connect to RabbitMQ after {attempt} retries.",
                        extra={
                            "service": service_name,
                            "host": self.rabbitmq_config.RABBITMQ_HOST,
                            "duration_ms": calculate_duration(start_time),
                        }
                    )
                raise ConnectionError("Failed to connect to RabbitMQ after retries.")

        except Exception as e:
            logging.error(
                f"Error in RabbitMQ connection: {e}",
                extra={
                    "service": service_name,
                    "host": self.rabbitmq_config.RABBITMQ_HOST,
                    "stack_trace": str(e),
                    "duration_ms": calculate_duration(start_time),
                }
            )
            raise CustomException(e, sys)


    def declare_queue(self, queue_name: str, durable: bool = True) -> None:
        """
        Declare a queue on the RabbitMQ server.

        Parameters
        ----------
        queue_name : str
            Name of the queue to declare.
        durable : bool, optional
            Whether the queue should survive broker restarts (default True).

        Raises
        ------
        CustomException
            If the queue declaration fails.

        Examples
        --------
        >>> client.declare_queue('task_queue')
        """
        start_time = time.perf_counter()
        try:
            assert self.channel is not None
            self.channel.queue_declare(queue=queue_name, durable=durable)
            logging.info(
                f"Declared queue: {queue_name}",
                extra={
                    "service": service_name,
                    "host": self.rabbitmq_config.RABBITMQ_HOST,
                    "duration_ms": calculate_duration(start_time),
                }
            )
        except Exception as e:
            logging.error(
                f"Failed to declare queue '{queue_name}': {e}",
                extra= {
                    "service": service_name,
                    "host": self.rabbitmq_config.RABBITMQ_HOST,
                    "stack_trace": str(e),
                    "duration_ms": calculate_duration(start_time),
                }
            )
            raise CustomException(e, sys)


    def publish(self, queue_name: str, message: dict) -> None:
        """
        Publish a message to a specified queue.

        Converts datetime objects in the message to ISO format automatically.

        Parameters
        ----------
        queue_name : str
            Target queue name.
        message : dict
            The message body (must be a dictionary).

        Raises
        ------
        CustomException
            If message publishing fails.

        Examples
        --------
        >>> client.publish('task_queue', {"task": "process_data"})
        """
        start_time = time.perf_counter()
        try:
            if not isinstance(message, dict):
                raise CustomException("Message must be a dict", sys)
            elif isinstance(message.get("published"), datetime):
                message["published"] = message["published"].isoformat()  # or .strftime("%Y-%m-%d")
            assert self.channel is not None
            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2  # Make message persistent
                )
            )
            logging.info(
                f"Message published: {message}",
                extra= {
                    "service": service_name,
                    "host": self.rabbitmq_config.RABBITMQ_HOST,
                    "duration_ms": calculate_duration(start_time)
                }

            )
        except Exception as e:
            logging.error(
                f"Error publishing message: {e}",
                extra= {
                    "service": service_name,
                    "host": self.rabbitmq_config.RABBITMQ_HOST,
                    "stack_trace": str(e),
                    "duration_ms": calculate_duration(start_time)
                }
            )
            raise CustomException(e, sys)


    def consume(
            self,
            queue_name: str,
            callback: Callable[[pika.channel.Channel, pika.spec.Basic.Deliver, pika.spec.BasicProperties, bytes], None],
            auto_ack: bool = False,
            prefetch_count: int = 1
        ) -> None:
        """
        Start consuming messages from a queue.

        Parameters
        ----------
        queue_name : str
            Queue to consume from.
        callback : callable
            Function to process messages. Signature:
            callback(channel, method, properties, body)
        auto_ack : bool, optional
            Automatically acknowledge messages (default False).
        prefetch_count : int, optional
            Number of messages to prefetch (default 1).

        Raises
        ------
        CustomException
            If consuming messages fails.
        """
        start_time = time.perf_counter()
        try:
            assert self.channel is not None
            self.channel.basic_qos(prefetch_count=prefetch_count)
            self.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=auto_ack)
            logging.info(
                f"Started consuming from queue: {queue_name}",
                extra= {
                    "service": service_name,
                    "host": self.rabbitmq_config.RABBITMQ_HOST,
                    "duration_ms": calculate_duration(start_time)
                }
            )
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logging.info(
                "Consumer interrupted by user.",
                extra= {
                    "service": service_name,
                    "host": self.rabbitmq_config.RABBITMQ_HOST,
                    "duration_ms": calculate_duration(start_time)
                }
            )
            self.close()
            return
        except ChannelClosedByBroker as e:
            logging.error(
                f"Channel closed by broker: {e}",
                extra= {
                    "service": service_name,
                    "host": self.rabbitmq_config.RABBITMQ_HOST,
                    "stack_trace": str(e),
                    "duration_ms": calculate_duration(start_time)
                }
            )
            self.close()
            raise CustomException(e, sys)
        except Exception as e:
            logging.error(
                f"Error during consuming messages: {e}",
                extra= {
                    "service": service_name,
                    "host": self.rabbitmq_config.RABBITMQ_HOST,
                    "stack_trace": str(e),
                    "duration_ms": calculate_duration(start_time)
                }
            )
            self.close()
            raise CustomException(e, sys)


    def close(self) -> None:
        """
        Gracefully close the channel and connection.

        Ensures all resources are released properly. Should be called when
        RabbitMQ operations are complete.

        Raises
        ------
        CustomException
            If closing the channel or connection fails.

        Examples
        --------
        >>> client.close()
        """
        start_time = time.perf_counter()
        try:
            if self.channel and self.channel.is_open:
                self.channel.close()
            if self.connection and self.connection.is_open:
                self.connection.close()
            logging.info(
                "RabbitMQ connection closed.",
                extra= {
                    "service": service_name,
                    "host": self.rabbitmq_config.RABBITMQ_HOST,
                    "duration_ms": calculate_duration(start_time)
                }
            )
        except Exception as e:
            logging.warning(
                f"Error while closing RabbitMQ connection: {e}",
                extra= {
                    "service": service_name,
                    "host": self.rabbitmq_config.RABBITMQ_HOST,
                    "stack_trace": str(e),
                    "duration_ms": calculate_duration(start_time)
                }
            )
            raise CustomException(e, sys)


    def __enter__(self) -> "RabbitMQClient":
        """
        Enter runtime context for `with` statement.

        Returns
        -------
        RabbitMQClient
            The client instance itself.

        Examples
        --------
        >>> with RabbitMQClient(config) as client:
        ...     client.declare_queue('my_queue')
        ...     client.publish('my_queue', {"message": "Hello"})
        """
        return self


    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Exit runtime context and close the connection.

        Parameters
        ----------
        exc_type : type
            Exception type, if any.
        exc_value : Exception
            Exception instance, if any.
        traceback : traceback
            Traceback object, if any.
        """
        self.close()
