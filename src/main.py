import sys
from pathlib import Path
from redis_service.middleware import RedisSessionMiddleware

sys.path.append(str(Path(__file__).resolve().parent))

import uvicorn
from fastapi import FastAPI
from core.routers import api_router

app = FastAPI(root_path="/api")

app.include_router(api_router)
app.add_middleware(RedisSessionMiddleware)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
