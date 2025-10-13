from typing import Annotated

from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from auth.deps import get_user_by_token
from core.deps import get_db_session
from rabbit.producer import publish_message
from .models import User
from .schemas import UserResponse, UserRegister
from .service import register_user

users_router = APIRouter()



@users_router.post("/register", response_model=UserResponse)
async def register_user_endpoint(body: UserRegister, db: Annotated[AsyncSession, Depends(get_db_session)],
                                 background_tasks: BackgroundTasks):
    new_user = await register_user(body, db)
    background_tasks.add_task(publish_message, 'Сущность пользователь создана')
    return UserResponse.model_validate(new_user)


@users_router.get("/me", response_model=UserResponse)
async def read_users_me_endpoint(current_user: Annotated[User, Depends(get_user_by_token)]):
    return UserResponse.model_validate(current_user, from_attributes=True)
