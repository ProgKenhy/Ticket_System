import pika
from typing import Optional
from core.settings import rabbit_settings
from pika.adapters.blocking_connection import BlockingChannel


class RabbitMQClient:
    """Клиент для RabbitMQ с конфигурацией из settings."""

    def __init__(
        self,
        host: str = rabbit_settings.HOST,
        port: int = rabbit_settings.PORT,
        user: str = rabbit_settings.USER,
        password: str = rabbit_settings.PASSWORD.get_secret_value(),
        queue_name: str = rabbit_settings.QUEUE_NAME,
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.queue_name = queue_name

        self._connection: Optional[pika.BlockingConnection] = None
        self._channel: Optional[BlockingChannel] = None

    def connect(self):
        """Создаёт подключение и канал, если их нет."""
        if self._connection and self._connection.is_open:
            return
        credentials = pika.PlainCredentials(self.user, self.password)
        params = pika.ConnectionParameters(host=self.host, port=self.port, credentials=credentials)
        self._connection = pika.BlockingConnection(params)
        self._channel = self._connection.channel()
        self._channel.queue_declare(queue=self.queue_name, durable=True)

    def publish(self, message: str):
        """Публикует сообщение."""
        if not self._connection or self._connection.is_closed:
            self.connect()

        self._channel.basic_publish(
            exchange="",
            routing_key=self.queue_name,
            body=message.encode() if isinstance(message, str) else message,
            properties=pika.BasicProperties(delivery_mode=2),
        )

    def close(self):
        if self._connection and self._connection.is_open:
            self._connection.close()
