"""add invoice soft delete

Revision ID: 6d41e7a1c8f2
Revises: 3c917b4a20f1
Create Date: 2026-06-19
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "6d41e7a1c8f2"
down_revision: Union[str, Sequence[str], None] = "3c917b4a20f1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "invoices",
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
    )
    op.create_index(
        op.f("ix_invoices_is_deleted"),
        "invoices",
        ["is_deleted"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_invoices_is_deleted"), table_name="invoices")
    op.drop_column("invoices", "is_deleted")
