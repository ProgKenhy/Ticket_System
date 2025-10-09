from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from users.models import User
from .utils import verify_password
from users.crud import get_user_by_login


async def authenticate_user(login: str, db: AsyncSession, password: str) -> Optional[User]:
    """Аутентификация пользователя по username/email и password"""
    user = await get_user_by_login(login=login, db=db)
    if not user or not verify_password(password, str(user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
