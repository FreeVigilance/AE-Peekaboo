# flake8: noqa WPS412
"""Роутеры мониторинга."""

from fastapi import APIRouter

from src.interfaces.api.routers.monitoring import monitoring

router = APIRouter()

router.include_router(monitoring.hc_router, tags=["Monitoring"])
