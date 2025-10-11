from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from .auth_session import update_session_when_login, delete_session
from .schemas import Token
from core.deps import get_db_session
from .utils import create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from .auth import authenticate_user

auth_router = APIRouter()


@auth_router.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: Annotated[AsyncSession, Depends(get_db_session)], request: Request) -> Token:
    """Ручка для входа пользователя по username/email и паролю с созданием access_token и обновлением информации о сессии"""
    user = await authenticate_user(form_data.username, db, form_data.password)
    await update_session_when_login(request, user.id) # noqa
    token_str = create_access_token(
        subject=str(user.id),
    )
    return Token(access_token=token_str, token_type="bearer")


@auth_router.post("/logout")
async def logout(response: Response, request: Request):
    """Выход пользователя - очистка сессии"""
    await delete_session(response=response, request=request)
    return {"message": "Logged out successfully"}
