from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from .settings import mysql_settings, settings


def get_async_engine():
    _async_engine = create_async_engine(
        mysql_settings.async_url,
        echo=settings.DEBUG,
        future=True,
        pool_pre_ping=True,
        pool_recycle=300,
        poolclass=NullPool if settings.ENVIRONMENT == "testing" else None,
    )
    return _async_engine


def get_async_session_factory(_async_engine):
    """Получение асинхронного движка для работы с бд (зависимости get_db_session)"""
    _async_session_factory = async_sessionmaker(
        _async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    return _async_session_factory
