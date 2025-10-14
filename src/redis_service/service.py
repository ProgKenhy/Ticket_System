import json
from typing import Callable

from core.settings import redis_settings
from core.logger import logger
from .utils import _serialize_result
import hashlib
from redis_service.client import RedisClient


def make_cache_key(prefix: str, *parts) -> str:
    """Создание ключа для словаря(кэш редис)"""
    key_base = "|".join(map(str, parts))
    hashed = hashlib.sha256(key_base.encode()).hexdigest()
    return f"{prefix}:{hashed}"


async def get_cached_or_set(redis_client: RedisClient, key: str, loader: Callable, ttl: int = redis_settings.TTL):
    """Получение данных из хэша либо добавление их при отсутствии"""
    try:
        cached_raw = await redis_client.get(key)
    except Exception as e:
        logger.error(f"Redis GET error", exc_info=e)
        return await loader()

    if cached_raw is not None:
        try:
            data = json.loads(cached_raw)
            logger.info(f"CACHE HIT {key}")
            return data
        except Exception as e:
            logger.error(f"JSON load failed for cached data", exc_info=e)
    result = await loader()
    serializable = await _serialize_result(result)
    try:
        await redis_client.setex(key, int(ttl), json.dumps(serializable, ensure_ascii=False))
        logger.info(f"CACHE SET {key}")
    except Exception as e:
        logger.error(f"Redis SETEX error", exc_info=e)
    return result
