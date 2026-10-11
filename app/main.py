from fastapi import FastAPI
from app.config.settings import settings
from app.api.router import api_router
from app.api.v1.repository import router as repository_router
from app.api.v1.chat import router as chat_router
from app.api.v1.agent import router as agent_router
from app.api.v1.change_request import (
    router as change_request_router
)

app=FastAPI(title=settings.APP_NAME, version="1.0.0")
app.include_router(api_router, prefix="/api/v1")
app.include_router(
    repository_router,
    prefix="/api/v1"
)
app.include_router(
    chat_router,
    prefix="/api/v1"
)
app.include_router(
    agent_router,
    prefix="/api/v1"
)
app.include_router(
    change_request_router,
    prefix="/api/v1"
)

@app.get("/")
def root():
    return {
        "app_name":settings.APP_NAME,
        "version":"1.0.0",
        "status":"running"
    }

