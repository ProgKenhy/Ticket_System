from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import Token
from core.deps import get_db_session
from .deps import get_user_by_token
from users.service import get_user_by_login
from .utils import verify_password, create_access_token
from fastapi.security import OAuth2PasswordRequestForm

from users.models import User

auth_router = APIRouter()


@auth_router.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db_session: Annotated[AsyncSession, Depends(get_db_session)]) -> Token:
    """Ручка для входа пользователя по username/email и паролю с созданием access_token"""
    user = await get_user_by_login(form_data.username, db_session)
    if not user or not verify_password(form_data.password, str(user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        subject=str(user.id),
    )
    return Token(access_token=token, token_type="bearer")


@auth_router.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_user_by_token)]):
    return current_user
