"""add report filters

Revision ID: 3c917b4a20f1
Revises: 9b7eb6f63a98
Create Date: 2026-06-18
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "3c917b4a20f1"
down_revision: Union[str, Sequence[str], None] = "9b7eb6f63a98"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("reports", sa.Column("filters_json", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("reports", "filters_json")
