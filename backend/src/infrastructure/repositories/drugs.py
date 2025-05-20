import sqlalchemy as sa

from src.infrastructure.models.public import Drug, SubmissionRule, TypeOfEvent
from src.infrastructure.repositories.base import BaseRepository


class DrugsRepo(BaseRepository):
    """Репозиторий для работы с таблицей drugs в БД."""

    table = Drug

    async def get_all_drugs(self):
        statement = sa.select(self.table)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_drug_info(self, drug_ids: list, words: list):
        stmt = (
            sa.select(
                Drug.trade_name,
                Drug.inn,
                Drug.obligation,
                SubmissionRule.source_countries,
                SubmissionRule.receiver,
                SubmissionRule.deadline_to_submit,
                SubmissionRule.format,
                SubmissionRule.other_procedures,
                TypeOfEvent.name.label("type_of_event"),
            )
            .outerjoin(SubmissionRule, SubmissionRule.routename == Drug.id)
            .outerjoin(
                TypeOfEvent, TypeOfEvent.id == SubmissionRule.type_of_event
            )
            .where(
                sa.or_
                    (
                    Drug.id.in_(drug_ids),
                    Drug.trade_name.in_(words),
                    Drug.inn.in_(words),
                )
            )
        )
        result = await self.session.execute(stmt)
        return result.fetchall()

