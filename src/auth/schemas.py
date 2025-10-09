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
