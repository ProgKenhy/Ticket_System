from fastapi import APIRouter
from fastapi.responses import JSONResponse
from auth.routers import auth_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])


@api_router.get("/health/")
async def health_check():
    """Проверка работоспособности приложения"""
    return JSONResponse(
        status_code=200,
        content={"status": "healthy", "service": "task_service"}
    )
