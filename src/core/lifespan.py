from fastapi import FastAPI
from contextlib import asynccontextmanager

from redis_service.client import RedisClient
from .clients import clients
from rabbit.producer import RabbitMQClient
from .logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    clients.rabbitmq = RabbitMQClient()
    clients.rabbitmq.connect()
    logger.info("RabbitMQ connected")

    clients.redis = RedisClient()
    await clients.redis.connect()

    yield

    if clients.rabbitmq:
        clients.rabbitmq.close()
        logger.info("RabbitMQ connection closed")

    if clients.redis:
        await clients.redis.close()
        logger.info("Redis connection closed")