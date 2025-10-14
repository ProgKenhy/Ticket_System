from typing import AsyncGenerator

from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from rabbit.producer import RabbitMQClient
from redis_service.client import RedisClient

async def get_rabbitmq(request: Request) -> RabbitMQClient:
    """Зависимость для RabbitMQ клиента."""
    rabbitmq = request.state.rabbitmq
    if not rabbitmq:
        raise HTTPException(status_code=500, detail="RabbitMQ client not initialized")
    return rabbitmq


async def get_redis_client(request: Request) -> RedisClient:
    """Зависимость для redis клиента."""
    redis_client = request.state.redis_client
    if not redis_client:
        raise HTTPException(status_code=500, detail="Redis client not initialized")
    return redis_client


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Получение сессии для работы с бд"""
    async_session_factory = request.state.async_session_factory
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
