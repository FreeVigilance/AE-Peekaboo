"""Основной маршрутизатор приложения секции мониторинга и проверки активности и доступности."""

import logging
from http import HTTPStatus

import sqlalchemy as sa
from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from src.interfaces.api.dependencies.session import get_session
from src.settings import settings

logger = logging.getLogger(__file__)


hc_router = APIRouter()


@hc_router.get("/healthcheck")
@hc_router.get("/liveness")
@hc_router.get("/readiness")
async def healthcheck(
    request: Request, session: AsyncSession = Depends(get_session)
) -> JSONResponse:
    """Healthcheck приложения. Проверяет готовность БД и других зависимостей."""
    response: dict[str, bool] = {"postgres": await check_pg(session)}

    status_code = status.HTTP_200_OK
    if response and not all(response.values()):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return JSONResponse(response, status_code=status_code)


async def check_pg(session: AsyncSession) -> bool:
    try:
        await session.execute(sa.text("SELECT 1"))
        return True
    except Exception:
        return False


@hc_router.get("/metrics")
async def metrics() -> Response:
    """Получение метрик приложения.

    Returns:
        Response: Возврат метрик

    """
    body, headers = settings.metrics.render()
    return Response(body, headers=headers, status_code=HTTPStatus.OK)
