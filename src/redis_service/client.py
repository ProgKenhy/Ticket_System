import redis.asyncio as aioredis
from core.settings import redis_settings

_redis_client = None


def get_redis_client():
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            redis_settings.async_url,
            decode_responses=True,
            password=redis_settings.PASSWORD,
        )
    return _redis_client