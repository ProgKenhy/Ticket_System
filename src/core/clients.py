from typing import Optional
from rabbit.producer import RabbitMQClient

class AppClients:
    rabbitmq: Optional[RabbitMQClient] = None

clients = AppClients()
