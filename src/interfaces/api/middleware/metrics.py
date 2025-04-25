"""Middleware для prometheus метрик приложения."""

import time
from collections.abc import Callable, MutableMapping
from typing import Any

from fastapi import Request, Response
from starlette.routing import Match, Mount

from src.settings import settings

MICROSECONDS_IN_A_SECOND = 1000000
SLASH = '/'
PATH = 'path'


async def collect_prometheus_metrics(request: Request, call_next: Callable) -> Response:
    route_name = get_route_name(request)
    if route_name is None:
        route_name = request.scope[PATH]

    request_start = time.perf_counter_ns()
    status_code = 500

    try:  # noqa: WPS501 - `finally` in `try` block without `except`
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        request_end = time.perf_counter_ns()
        request_duration = (
            request_end - request_start
        ) // MICROSECONDS_IN_A_SECOND  # В миллисекундах
        labels = {
            'method': request.method,
            'path': route_name,
            'status_code': str(status_code),
            'service': settings.app.name,

        }

        settings.metrics.http_requests_latency.observe(
            labels,  # type: ignore
            request_duration,
        )


# unified copy-paste from
# https://github.com/elastic/apm-agent-python/blob/7d09ed8959afb2f2bd2e011969d2a6d3fdd6cd28/elasticapm/contrib/starlette/__init__.py#L229
def get_route_name(request: Request) -> str | None:
    """Извлекает имя маршрута из объекта запроса.

    Args:
        request (Request): Объект запроса FastAPI.

    Returns:
        Optional[str]: Имя маршрута, если найдено, иначе None.
    """
    app = request.app
    scope = request.scope
    routes = app.routes
    route_name = _get_route_name(scope, routes)

    # Starlette magically redirects requests if the path matches a route name with a trailing slash
    # appended or removed. To not spam the transaction names list, we do the same here and put these
    # redirects all in the same "redirect trailing slashes" transaction name
    if not route_name and app.router.redirect_slashes and scope[PATH] != SLASH:
        redirect_scope = dict(scope)
        if scope[PATH].endswith(SLASH):
            redirect_scope[PATH] = scope[PATH][:-1]
            trim = True
        else:
            redirect_scope[PATH] = scope[PATH] + SLASH
            trim = False

        route_name = _get_route_name(redirect_scope, routes)
        if route_name is not None:
            route_name += SLASH if trim else route_name[:-1]
    return route_name


def _get_route_name(
    scope: MutableMapping[str, Any],
    routes: list,
    route_name: str | None = None,
) -> str | None:
    for route in routes:
        match, child_scope = route.matches(scope)
        if match == Match.FULL:
            route_name = route.path
            child_scope = {**scope, **child_scope}
            if isinstance(route, Mount) and route.routes:
                child_route_name = _get_route_name(child_scope, route.routes, route_name)
                if child_route_name is None:
                    route_name = None
                else:
                    route_name += child_route_name  # type: ignore[operator]
            return route_name
        if match == Match.PARTIAL and route_name is None:
            route_name = route.path
    return None
