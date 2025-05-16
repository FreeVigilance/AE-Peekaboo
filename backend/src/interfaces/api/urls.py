"""
Основной маршрутизатор приложения.

Модуль содержит основной объект маршрутизатора `router`, который включает другие маршруты,
"""

from fastapi import APIRouter

from src.interfaces.api.routers import api, monitoring

router = APIRouter()
router.include_router(api.router)
router.include_router(monitoring.router)
