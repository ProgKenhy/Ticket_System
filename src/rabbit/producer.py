import time
import pika
from typing import Optional
from pika.adapters.blocking_connection import BlockingChannel
from core.settings import rabbit_settings
from core.logger import logger
from pika import exceptions as pika_exceptions


class RabbitMQClient:
    """Устойчивый клиент для RabbitMQ с автопереподключением и безопасным закрытием."""

    def __init__(
        self,
        host: str = rabbit_settings.HOST,
        port: int = rabbit_settings.PORT,
        user: str = rabbit_settings.USER,
        password: str = rabbit_settings.PASSWORD.get_secret_value(),
        queue_name: str = rabbit_settings.QUEUE_NAME,
        max_retries: int = 5,
        retry_delay: int = 3,
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.queue_name = queue_name
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        self._connection: Optional[pika.BlockingConnection] = None
        self._channel: Optional[BlockingChannel] = None

    def connect(self):
        """Создаёт подключение и канал, если их нет."""
        if self._connection and self._connection.is_open:
            return

        credentials = pika.PlainCredentials(self.user, self.password)
        params = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            credentials=credentials,
            heartbeat=30,
            blocked_connection_timeout=10,
            connection_attempts=3,
            retry_delay=2,
        )

        for attempt in range(1, self.max_retries + 1):
            try:
                self._connection = pika.BlockingConnection(params)
                self._channel = self._connection.channel()
                self._channel.queue_declare(queue=self.queue_name, durable=True)
                logger.info(f"Connected to RabbitMQ (attempt {attempt})")
                return
            except pika_exceptions.AMQPConnectionError as e:
                logger.warning(f"RabbitMQ connection failed (attempt {attempt}/{self.max_retries}): {e}")
                time.sleep(self.retry_delay)

        raise RuntimeError("Failed to connect to RabbitMQ after several attempts")

    def publish(self, message: str):
        """Публикует сообщение с переподключением при необходимости"""
        try:
            if not self._connection or self._connection.is_closed:
                self.connect()
            self._channel.basic_publish(
                exchange="",
                routing_key=self.queue_name,
                body=message.encode() if isinstance(message, str) else message,
                properties=pika.BasicProperties(delivery_mode=2),
            )
        except pika_exceptions.AMQPConnectionError:
            logger.warning("RabbitMQ connection lost, reconnecting...")
            self.connect()
            self.publish(message)

    def close(self):
        """Безопасно закрывает соединение."""
        try:
            if self._connection and self._connection.is_open:
                self._connection.close()
                logger.info("RabbitMQ connection closed")
        except pika_exceptions.StreamLostError:
            logger.warning("RabbitMQ connection already lost before close()")
        except Exception as e:
            logger.warning(f"Failed to close RabbitMQ connection: {e}")
