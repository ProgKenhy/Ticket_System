import uuid
import json
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from core.logger import logger

from redis_service.service import redis_client
from core.settings import settings

SESSION_COOKIE = "session_id" # !TODO вынести в settings
SESSION_PREFIX = "session:"
SESSION_TTL = 3600

def _now_iso():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()

class RedisSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        session_id = request.cookies.get(SESSION_COOKIE)
        is_new = False

        if not session_id:
            session_id = str(uuid.uuid4())
            session = {"created_at": _now_iso(), "last_activity": _now_iso()}
            is_new = True
        else:
            try:
                raw = await redis_client.get(SESSION_PREFIX + session_id)
                session = json.loads(raw) if raw else {"created_at": _now_iso()}
            except Exception as e:
                logger.error(f"Redis GET error", exc_info=e)
                session = {"created_at": _now_iso()}

        request.state.session = session
        request.state._session_id = session_id
        request.state.session_is_dirty = False

        response: Response = await call_next(request)

        session["last_activity"] = _now_iso()
        request.state.session_is_dirty = True

        try:
            if request.state.session_is_dirty:
                await redis_client.setex(
                    SESSION_PREFIX + session_id,
                    SESSION_TTL,
                    json.dumps(request.state.session, ensure_ascii=False),
                )
            if is_new or SESSION_COOKIE not in request.cookies:
                response.set_cookie(
                    SESSION_COOKIE,
                    session_id,
                    httponly=True,
                    samesite="lax",
                    secure=(settings.ENVIRONMENT == "production"),
                    max_age=SESSION_TTL,
                    path="/",
                )
        except Exception as e:
            logger.error(f"Redis SETEX error", exc_info=e)

        return response
