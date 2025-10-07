from typing import Optional

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from users.models import User


async def get_user_by_login(login: str,
                   db_session: AsyncSession) -> Optional[User]:
    """Получение пользователя по username(email) из БД"""
    stmt = select(User).where(or_(User.username == login, User.email == login))
    result = await db_session.execute(stmt)
    user = result.scalar_one_or_none()
    return user