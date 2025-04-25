"""Модуль инициализации приложения FastAPI."""
import pickle
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import ahocorasick
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine
from starlette.middleware.cors import CORSMiddleware

from src.interfaces.api.middleware.metrics import collect_prometheus_metrics
from src.settings import settings

from .urls import router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Асинхронный контекстный менеджер для управления жизненным циклом приложения.

    Args:
        app (FastAPI):  объект приложения FastAPI

    Yields:
        None:
    """
    # TODO: move somewhere
    # init resources
    automation: ahocorasick.Automaton = ahocorasick.load("aho_corasick_medications2.model",
                                                         pickle.loads)
    app.state.automaton = automation

    yield

    # release resources


app = FastAPI(
    lifespan=lifespan,
)
app.include_router(router)
# TODO: add middlewares
app.middleware('http')(collect_prometheus_metrics)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
