from fastapi import FastAPI
from contextlib import asynccontextmanager
from .clients import clients
from rabbit.producer import RabbitMQClient
from .logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    clients.rabbitmq = RabbitMQClient()
    clients.rabbitmq.connect()
    logger.info("RabbitMQ connected")

    yield

    if clients.rabbitmq:
        clients.rabbitmq.close()
        logger.info("RabbitMQ connection closed")