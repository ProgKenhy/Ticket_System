from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from sqlalchemy.pool import NullPool

from .settings import settings


def import_all_models() -> None:
    import users.models  # noqa: F401
    import tickets.models  # noqa: F401


# импортируем модели ДО работы с metadata/engine
import_all_models()

async_engine = create_async_engine(
    settings.database.async_url,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_recycle=300,
    # Для тестов используем NullPool, чтобы изолировать тесты
    poolclass=NullPool if settings.ENVIRONMENT == "testing" else None
)

async_session_factory = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)
