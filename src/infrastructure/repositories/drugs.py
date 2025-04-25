"""Модуль содержащий репозиторий Событий."""
import sqlalchemy as sa
from src.infrastructure.models import drugs
from src.infrastructure.repositories.base import BaseRepository


class DrugsRepo(BaseRepository):
    """Репозиторий для работы с таблицей drugs в БД."""

    table = drugs

    async def get_all_trade_names(self):
        statement = sa.select(self.table.c.trade_name)
        result = await self.session.execute(statement)
        return result.scalars().all()

