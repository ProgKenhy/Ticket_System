from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import Token
from core.deps import get_db_session
from .utils import create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from .auth import authenticate_user

auth_router = APIRouter()


@auth_router.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: Annotated[AsyncSession, Depends(get_db_session)]) -> Token:
    """Ручка для входа пользователя по username/email и паролю с созданием access_token"""
    user = await authenticate_user(form_data.username, db, form_data.password)
    token_str = create_access_token(
        subject=str(user.id),
    )
    return Token(access_token=token_str, token_type="bearer")
