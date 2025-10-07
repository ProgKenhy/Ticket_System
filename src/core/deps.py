from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from .database import async_session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Получение сессии для работы с бд"""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
