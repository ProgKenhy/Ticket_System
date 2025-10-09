from fastapi import APIRouter
from fastapi.responses import JSONResponse
from auth.routers import auth_router
from users.routers import users_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])


@api_router.get("/health/")
async def health_check():
    """Проверка работоспособности приложения"""
    return JSONResponse(
        status_code=200,
        content={"status": "healthy", "service": "task_service"}
    )
