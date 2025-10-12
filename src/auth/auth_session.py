from datetime import datetime, timezone
from fastapi import Request, Response

from redis.service import redis_client

SESSION_COOKIE = "session_id" # !TODO вынести в settings
SESSION_PREFIX = "session:"
SESSION_TTL = 3600

def _now_iso():
    return datetime.now(timezone.utc).isoformat()


async def update_session_when_login(request: Request, user_id: int) -> None:
    """
    Обновляет существующую сессию, добавляя данные пользователя.
    Сессия уже создана middleware, мы просто её обновляем.
    """
    session = request.state.session

    session.update({
        "user_id": user_id,
        "is_authenticated": True,
        "authenticated_at": _now_iso()
    })

    request.state.session_is_dirty = True


async def delete_session(response: Response, request: Request) -> None:
    sid = request.cookies.get(SESSION_COOKIE)
    if sid:
        try:
            await redis_client.delete(SESSION_PREFIX + sid)
        except Exception(BaseException):
            pass
    response.delete_cookie(SESSION_COOKIE, path="/")
