import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from app.config import settings, TORTOISE_ORM
from app.routers import monitoring, thresholds, ponds, ws

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(monitoring.router)
app.include_router(thresholds.router)
app.include_router(ponds.router)
app.include_router(ws.router)


@app.get("/", tags=["根路径"])
async def root():
    return {
        "name": settings.APP_NAME,
        "version": "2.0.0",
        "status": "running",
        "features": ["realtime-alert", "websocket"]
    }


@app.get("/health", tags=["健康检查"])
async def health_check():
    from app.ws_manager import alert_manager
    return {
        "status": "healthy",
        "ws_clients": len(alert_manager.active_connections)
    }


register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,
)
