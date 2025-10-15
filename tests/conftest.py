import os
import sys

from sqlalchemy.orm import clear_mappers

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import AsyncMock

from main import app
from core.deps import get_db_session, get_redis_client, get_rabbitmq
from auth.deps import get_user_id_from_token
from db.base import MyBaseModel as Base
from db.init_models import import_all_models





@pytest.fixture(scope="session")
def event_loop():
    """Один event loop на всю сессию pytest."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_engine():
    """Создает временную SQLite базу данных."""
    # clear_mappers()
    from users.models import User
    from tickets.models import Ticket
    # import_all_models()
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        Base.metadata.clear()
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(test_engine):
    """Создает сессию SQLAlchemy для теста."""
    async_session_maker = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
def mock_redis():
    """Мок Redis клиента."""
    mock = AsyncMock()
    mock.get.return_value = None
    mock.setex.return_value = True
    mock.delete.return_value = 1
    mock.ping.return_value = True
    return mock


@pytest.fixture(scope="function")
def mock_rabbitmq():
    """Мок RabbitMQ клиента."""
    mock = AsyncMock()
    mock.connect.return_value = None
    mock.close.return_value = None
    mock.publish.return_value = None
    return mock


@pytest.fixture(scope="function")
async def client(test_engine, mock_redis, mock_rabbitmq):
    """
    Создает тестовый HTTP клиент:
    - заменяет зависимости FastAPI
    - подменяет clients.redis и clients.rabbitmq моками
    """

    async def override_get_db():
        async_session_maker = async_sessionmaker(
            test_engine, class_=AsyncSession, expire_on_commit=False
        )
        async with async_session_maker() as session:
            yield session

    async def override_get_user_id():
        return 1

    app.dependency_overrides[get_db_session] = override_get_db
    app.dependency_overrides[get_user_id_from_token] = override_get_user_id
    app.dependency_overrides[get_redis_client] = lambda: mock_redis
    app.dependency_overrides[get_rabbitmq] = lambda: mock_rabbitmq
    app.state.redis_client = mock_redis

    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def authenticated_client(client):
    """HTTP клиент с тестовым токеном."""
    client.headers.update({"Authorization": "Bearer test_token"})
    yield client
