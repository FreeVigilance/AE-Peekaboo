"""tables update

Revision ID: abc5b19996f8
Revises: b6e35bcacbd5
Create Date: 2025-05-09 17:59:01.981781

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "abc5b19996f8"
down_revision = "b6e35bcacbd5"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "submission_rules",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("routename", sa.UUID(), nullable=True),
        sa.Column("source_countries", sa.String(), nullable=True),
        sa.Column("receiver", sa.String(), nullable=True),
        sa.Column("deadline_to_submit", sa.DateTime(), nullable=True),
        sa.Column("format", sa.String(), nullable=True),
        sa.Column("other_procedures", sa.String(), nullable=True),
        sa.Column("type_of_event", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["routename"],
            ["public.drugs.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="public",
    )
    op.create_table(
        "type_of_event",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("inn_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["inn_id"],
            ["public.submission_rules.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="public",
    )
    op.add_column("drugs", sa.Column("inn", sa.String(), nullable=True))
    op.add_column("drugs", sa.Column("oblication", sa.String(), nullable=True))
    op.add_column(
        "drugs", sa.Column("release_forms", sa.String(), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("drugs", "release_forms")
    op.drop_column("drugs", "oblication")
    op.drop_column("drugs", "inn")
    op.drop_table("type_of_event", schema="public")
    op.drop_table("submission_rules", schema="public")
    # ### end Alembic commands ###
