import json
from pydantic import BaseModel


def _now_iso():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


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
