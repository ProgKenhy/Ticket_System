from typing import TypedDict, AsyncIterator, cast

from fastapi import FastAPI
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from redis_service.client import RedisClient
from rabbit.producer import RabbitMQClient
from .logger import logger
from db.database import get_async_engine, get_async_session_factory
from db.init_models import import_all_models


class AppState(TypedDict):
    async_session_factory: async_sessionmaker[AsyncSession]
    redis: RedisClient
    rabbitmq: RabbitMQClient

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[AppState]:
    import_all_models()

    async_engine = get_async_engine()
    async_session_factory = get_async_session_factory(async_engine)

    redis = RedisClient()
    await redis.connect()
    redis_client = redis.client

    rabbitmq = RabbitMQClient()
    rabbitmq.connect()

    logger.info("Dependencies initialized")

    yield cast(
        AppState,
        {
            "async_session_factory": async_session_factory,
            "redis_client": redis_client,
            "rabbitmq": rabbitmq,
        },
    )

    logger.info("Shutting down dependencies...")
    rabbitmq.close()
    await redis.close()
    await async_engine.dispose()