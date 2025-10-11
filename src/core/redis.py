import json
from typing import Callable

import redis.asyncio as aioredis
from pydantic import BaseModel

from .settings import redis_settings

import hashlib

redis_client = aioredis.from_url(redis_settings.async_url, decode_responses=True, password=redis_settings.PASSWORD)

async def _normalize_for_json(obj):
    """Преобразует объект в JSON-сериализуемую структуру."""
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "as_dict") and callable(obj.as_dict):
        return obj.as_dict()
    if hasattr(obj, "__dict__"):
        result = {}
        for k, v in obj.__dict__.items():
            if k.startswith("_"):
                continue
            try:
                json.dumps(v)
                result[k] = v
            except TypeError:
                result[k] = str(v)
        return result
    return obj

async def _serialize_result(result):
    """Возвращает JSON-сериализуемую структуру: если list -> список сериализованных элементов."""
    if isinstance(result, list):
        out = []
        for item in result:
            out.append(await _normalize_for_json(item))
        return out
    return await _normalize_for_json(result)


def make_cache_key(prefix: str, *parts) -> str:
    key_base = "|".join(map(str, parts))
    hashed = hashlib.sha256(key_base.encode()).hexdigest()
    return f"{prefix}:{hashed}"

async def get_cached_or_set(key: str, loader: Callable, ttl: int = redis_settings.TTL):
    """Получение данных из хэша либо добавление их при отсутствии"""
    try:
        cached_raw = await redis_client.get(key)
    except Exception as e:
        print("Redis GET error:", e) # в дальнейшем можно реализовать logger
        return await loader()

    if cached_raw is not None:
        try:
            data = json.loads(cached_raw)
            print("CACHE HIT", key)
            return data
        except Exception as e:
            print("JSON load failed for cached data:", e)
    result = await loader()
    serializable = await _serialize_result(result)
    try:
        await redis_client.setex(key, int(ttl), json.dumps(serializable, ensure_ascii=False))
        print("CACHE SET", key)
    except Exception as e:
        print("Redis SETEX error:", e)
    return result