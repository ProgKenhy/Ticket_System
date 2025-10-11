from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.ext.asyncio import AsyncSession

from core.deps import get_db_session
from users.models import User
from .utils import decode_token
from users.crud import get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


async def get_user_id_from_token(token: str = Depends(oauth2_scheme)) -> Optional[int]:
    """Получение user_id из Token"""
    token_data = decode_token(token)
    return int(token_data.sub)


async def get_user_by_token(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Annotated[AsyncSession, Depends(get_db_session)],
) -> Optional[User]:
    """Получение текущего пользователя по Token"""
    token_data = decode_token(token)

    user = await get_user_by_id(user_id=int(token_data.sub), db=db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
