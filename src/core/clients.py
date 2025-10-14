from typing import Optional
from rabbit.producer import RabbitMQClient
from redis_service.client import RedisClient

class AppClients:
    rabbitmq: Optional[RabbitMQClient] = None
    redis: Optional[RedisClient] = None

clients = AppClients()
