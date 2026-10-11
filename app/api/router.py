from fastapi import APIRouter
from app.api.v1.repository import router as repository_router
from app.api.v1.chat import router as chat_router

api_router= APIRouter()
api_router.include_router(repository_router)
from app.api.v1.chat import router as chat_router