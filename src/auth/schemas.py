from typing import Optional

from pydantic import BaseModel
from datetime import datetime


class Token(BaseModel):
    """Модель Token"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Модель данных Token"""
    sub: str
    exp: datetime
    type: str


class SessionData(BaseModel):
    """Модель данных сессии"""
    created_at: str
    is_authenticated: bool = False

    user_id: Optional[int] = None
    email: Optional[str] = None
    username: Optional[str] = None


class SessionCreate(SessionData):
    """Модель для создания новой сессии"""
    pass

class SessionUpdate(BaseModel):
    """Модель для обновления сессии"""
    user_id: Optional[int] = None
    email: Optional[str] = None
    username: Optional[str] = None
    is_authenticated: Optional[bool] = None