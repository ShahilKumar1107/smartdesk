# routes/__init__.py — Registers all route files

from fastapi import APIRouter
from app.api.routes import health
from app.api.routes import auth
from app.api.routes import chat

api_router = APIRouter()

api_router.include_router(health.router, prefix="/api/v1")
api_router.include_router(auth.router, prefix="/api/v1")
api_router.include_router(chat.router, prefix="/api/v1")