from fastapi import APIRouter

from app.api.routes import items, login, users

from app.core.config import settings
api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router)
api_router.include_router(items.router, prefix="/items", tags=["items"])
