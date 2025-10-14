import redis.asyncio as aioredis
from core.settings import redis_settings
from core.logger import logger


class RedisClient:
    """Асинхронный клиент Redis с управлением жизненным циклом"""
    def __init__(self):
        self._client: aioredis.Redis | None = None

    async def connect(self):
        """Подключение к Redis"""
        if self._client:
            return self._client  # Уже подключён

        self._client = aioredis.from_url(
            redis_settings.async_url,
            decode_responses=True,
            password=redis_settings.PASSWORD,
        )

        try:
            await self._client.ping()
            logger.info("Redis connected")
        except Exception as e:
            logger.error("Redis connection failed", exc_info=e)
            self._client = None

        return self._client

    async def close(self):
        """Закрытие соединения"""
        if self._client:
            await self._client.close()
            logger.info("Redis connection closed")
            self._client = None

    @property
    def client(self) -> aioredis.Redis:
        """Возвращает активный клиент"""
        if not self._client:
            raise RuntimeError("Redis client not connected")
        return self._client
