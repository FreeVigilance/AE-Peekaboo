# flake8: noqa WPS412
"""
Маршрутизатор приложения.

Модуль содержит основной объект маршрутизатора `router`, который включает другие маршруты,
"""

from fastapi import APIRouter

from src.interfaces.api.routers.api import v1

router = APIRouter()
router.include_router(v1.router, prefix='/api/v1')
