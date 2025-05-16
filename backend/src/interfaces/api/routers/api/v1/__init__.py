# flake8: noqa WPS412
"""
Основной маршрутизатор приложения Первой версии (V1).

Модуль содержит основной объект маршрутизатора `router`, который включает другие маршруты,
"""

from fastapi import APIRouter

from src.interfaces.api.routers.api.v1 import aho, auth, text_processing

router = APIRouter()


router.include_router(text_processing.router, tags=["Text Processing"])
router.include_router(aho.router, tags=["Aho"])
router.include_router(auth.router, tags=["Auth"])
