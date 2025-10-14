from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_async_engine


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Получение сессии для работы с бд"""
    _, async_session_factory = get_async_engine()
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
