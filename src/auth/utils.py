from datetime import datetime, timedelta, UTC
from typing import Any, Optional

from core.settings import auth_settings
from pwdlib import PasswordHash
from fastapi import HTTPException, status
from .schemas import TokenData

import jwt

pwd_context = PasswordHash.recommended()
ACCESS_TOKEN_EXPIRE_MINUTES: int = auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES
SECRET_KEY: str = auth_settings.SECRET_KEY.get_secret_value()
JWT_ALG: str = auth_settings.JWT_ALG


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Верификация пароля"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Получение хэша пароля"""
    return pwd_context.hash(password)


def create_access_token(
        subject: str,
        expires_delta: float = ACCESS_TOKEN_EXPIRE_MINUTES,
        additional_data: Optional[dict[str, Any]] = None,
) -> str:
    """Создание access token"""
    if not subject:
        raise ValueError("Subject cannot be empty")

    expire = datetime.now(UTC) + timedelta(minutes=expires_delta)
    token_data = TokenData(sub=subject, exp=expire, type="access")

    payload = token_data.model_dump()
    if additional_data:
        payload.update(additional_data)

    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALG)


def decode_token(token: str) -> TokenData:
    """Декодирование токена"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALG])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not {"sub", "exp", "type"} <= payload.keys():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token structure",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenData.model_validate(payload)
