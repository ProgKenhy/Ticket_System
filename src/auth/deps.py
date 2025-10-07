from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from users.models import User
from .utils import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_user_by_token(
        token: Annotated[str, Depends(oauth2_scheme)],
        db_session: AsyncSession,
) -> User:
    """Получение текущего пользователя по Token"""
    token_data = decode_token(token)

    stmt = select(User).where(User.id == int(token_data.sub))
    user = (await db_session.execute(stmt)).scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

