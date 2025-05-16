"""Содержит зависимость для получения сессии базы данных."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.session import async_session_factory


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Асинхронная зависимость для получения сессии базы данных.

    Yields:
        AsyncSession

    Raises:
        Exception: Исключения, возникшие во время выполнения транзакции.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
