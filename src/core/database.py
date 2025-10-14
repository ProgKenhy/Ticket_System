from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from .settings import mysql_settings, settings


def import_all_models() -> None:
    import users.models  # noqa: F401
    import tickets.models  # noqa: F401


import_all_models()

_async_engine = None
_async_session_factory = None


def get_async_engine():
    """Получение асинхронного движка для работы с бд (зависимости get_db_session)"""
    global _async_engine, _async_session_factory
    if _async_engine is None:
        _async_engine = create_async_engine(
            mysql_settings.async_url,
            echo=settings.DEBUG,
            future=True,
            pool_pre_ping=True,
            pool_recycle=300,
            poolclass=NullPool if settings.ENVIRONMENT == "testing" else None,
        )
        _async_session_factory = async_sessionmaker(
            _async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )
    return _async_engine, _async_session_factory
