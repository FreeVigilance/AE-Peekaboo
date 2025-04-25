"""Содержит базовый репозиторий."""

from typing import Any

import sqlalchemy as sa
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.interfaces.api.dependencies.session import get_session


class BaseRepository:
    """Базовый репозиторий для работы с таблицей в БД."""

    table: sa.Table

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        self._session = session

    @property
    def session(self) -> AsyncSession:
        """Возвращает асинхронную сессию SQLAlchemy.

        Returns:
            AsyncSession: Асинхронная сессия.
        """
        return self._session

    async def create(self, **kwargs: Any) -> sa.Row | None:  # type: ignore
        """Создает новую запись в базе данных.

        Args:
            **kwargs (Any): Данные для вставки.

        Returns:
            BaseModel: Созданная запись модели.
        """
        statement = sa.insert(self.table).values(**kwargs).returning(self.table)
        result_obj = await self.session.execute(statement)
        await self.session.flush()
        return result_obj.fetchone()

    async def filter(
            self,
            *args: Any,
            limit: int = 10,
            offset: int = 0,
            order_by: list[tuple[str, Any]] | None = None,
            **kwargs: Any,
    ) -> list[sa.Row]:
        """Получение списка объектов.

        Args:
            *args: Аргументы для фильтрации.   # noqa: RST210, RST213
            limit (int): Ограничение количества возвращаемых объектов. Defaults to 10.
            offset (int): Смещение списка объектов. Defaults to 0.
            order_by (list[tuple[str, Any]] | None): Столбцы для сортировки.
            **kwargs: Дополнительные параметры для фильтрации.   # noqa: RST210

        Returns:
            List[ModelType]: Список объектов.
        """
        statement = sa.select(self.table).filter(*args).filter_by(**kwargs).limit(limit).offset(
            offset)  # type: ignore  # noqa: E501, WPS221
        # Добавление сортировки, если указаны поля для сортировки
        if order_by:
            for field in order_by:
                statement = statement.order_by(field[1](field[0]))  # noqa: E501, WPS221
        models_data = await self.session.execute(statement)
        return models_data if models_data else []

    async def get(self, *args: Any, **kwargs: Any) -> sa.Row | None:
        """Получение данных объекта.

        Args:
            *args: Аргументы для поиска объекта.   # noqa: RST210, RST213
            **kwargs: Дополнительные параметры для поиска объекта.   # noqa: RST210

        Returns:
            Optional[ModelType]: Найденный объект или None, если объект не найден.
        """
        statement = sa.select(self.table).filter(*args).filter_by(**kwargs)
        model_data = await self.session.execute(statement)
        return model_data.fetchone() if model_data else None

