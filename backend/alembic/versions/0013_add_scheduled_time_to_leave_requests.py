"""add scheduled_time to leave_requests

Revision ID: 0013
Revises: 0012
Create Date: 2026-07-05

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0013"
down_revision: Union[str, None] = "0012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("leave_requests", sa.Column("scheduled_time", sa.Time(), nullable=True))


def downgrade() -> None:
    op.drop_column("leave_requests", "scheduled_time")
