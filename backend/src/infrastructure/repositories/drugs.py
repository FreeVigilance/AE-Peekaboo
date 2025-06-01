from datetime import datetime

import sqlalchemy as sa

from src.infrastructure.models.public import Drug, SubmissionRule, TypeOfEvent, SubmissionRuleDrug
from src.infrastructure.repositories.base import BaseRepository


class DrugsRepo(BaseRepository):
    """Репозиторий для работы с таблицей drugs в БД."""

    table = Drug

    async def get_all_drugs(self):
        statement = sa.select(self.table)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_drug_info(self, drug_ids: list, words: list):
        now = datetime.now()
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
                SubmissionRule.valid_start_date,
                SubmissionRule.valid_end_date,
                TypeOfEvent.name.label("type_of_event"),
            )
            .join(
                SubmissionRuleDrug,
                SubmissionRuleDrug.drug_id == Drug.id,
                isouter=True
            )
            .join(
                SubmissionRule,
                SubmissionRule.id == SubmissionRuleDrug.submission_rule_id,
                isouter=True
            )
            .join(
                TypeOfEvent,
                TypeOfEvent.id == SubmissionRule.type_of_event,
                isouter=True
            )
            .where(
                sa.and_(
                    sa.or_(
                        Drug.id.in_(drug_ids),
                        Drug.trade_name.in_(words),
                        Drug.inn.in_(words),
                    ),
                    sa.or_(
                        sa.and_(
                            SubmissionRule.valid_start_date <= now,
                            SubmissionRule.valid_end_date >= now,
                        ),
                        sa.and_(
                            SubmissionRule.valid_start_date.is_(None),
                            SubmissionRule.valid_end_date.is_(None),
                        ),
                    )

                )
            )
        )
        result = await self.session.execute(stmt)
        return result.fetchall()
