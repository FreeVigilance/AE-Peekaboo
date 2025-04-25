"""Создание sqlalchemy engine и async_session_factory."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.settings import settings

engine = create_async_engine(
    settings.db.connection_string,
    future=True,
    pool_timeout=settings.db.connection_timeout,
    pool_size=settings.db.min_pool_size,
    max_overflow=settings.db.max_pool_size - settings.db.min_pool_size,
)

async_session_factory = sessionmaker(bind=engine, class_=AsyncSession)
