from typing import AsyncGenerator

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from rabbit.producer import RabbitMQClient
from .database import get_async_engine
from .clients import clients

async def get_rabbitmq() -> RabbitMQClient:
    """Зависимость для RabbitMQ клиента."""
    if not clients.rabbitmq:
        raise HTTPException(status_code=500, detail="RabbitMQ client not initialized")
    return clients.rabbitmq


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Получение сессии для работы с бд"""
    _, async_session_factory = get_async_engine()
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
