"""Модуль инициализации приложения FastAPI."""

import logging
import pickle
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import ahocorasick
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.interfaces.api.middleware.metrics import collect_prometheus_metrics
from src.settings import settings

from ...infrastructure.session import engine
from .admin import (
    DrugAdmin,
    DrugsAdmin,
    SQLAdminAuthenticationBackend,
    SubmissionAdmin,
    TypeOfEventAdmin,
    UserAdmin,
    SubmissionRuleDrugAdmin,
)
from .urls import router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Асинхронный контекстный менеджер для управления жизненным циклом приложения.

    Args:
        app (FastAPI):  объект приложения FastAPI

    Yields:
        None:
    """
    automation: ahocorasick.Automaton = ahocorasick.load(
        "./assets/aho_corasick_medications3.model", pickle.loads
    )
    app.state.automaton = automation

    yield


app = FastAPI(
    lifespan=lifespan,
)
app.include_router(router)
app.middleware("http")(collect_prometheus_metrics)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

admin = DrugsAdmin(
    app,
    engine,
    authentication_backend=SQLAdminAuthenticationBackend(
        settings.app.secret_key
    ),
)

admin.add_view(DrugAdmin)
admin.add_view(SubmissionAdmin)
admin.add_view(TypeOfEventAdmin)
admin.add_view(UserAdmin)
admin.add_view(SubmissionRuleDrugAdmin)
