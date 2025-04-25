"""Мета-данные для схемы 'public' в базе данных."""

import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

meta = sa.MetaData(schema='public')

drugs = sa.Table(
    'drugs',
    meta,
    sa.Column(
        'id',
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    ),
    sa.Column('trade_name', sa.String, nullable=False),
)
