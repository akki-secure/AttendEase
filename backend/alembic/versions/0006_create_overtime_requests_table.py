"""create overtime_requests table

Revision ID: 0006
Revises: 0005
Create Date: 2026-05-24

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "overtime_requests",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("start_time", sa.DateTime(), nullable=False),
        sa.Column("end_time", sa.DateTime(), nullable=False),
        sa.Column("minutes", sa.Integer(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="PENDING"),
        sa.Column("reviewer_id", sa.Integer(), nullable=True),
        sa.Column("reviewer_comment", sa.Text(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("(CURRENT_TIMESTAMP)")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("(CURRENT_TIMESTAMP)")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["reviewer_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_overtime_requests_user_id", "overtime_requests", ["user_id"])
    op.create_index("ix_overtime_requests_status", "overtime_requests", ["status"])
    op.create_index("ix_overtime_requests_date", "overtime_requests", ["date"])


def downgrade() -> None:
    op.drop_index("ix_overtime_requests_date", table_name="overtime_requests")
    op.drop_index("ix_overtime_requests_status", table_name="overtime_requests")
    op.drop_index("ix_overtime_requests_user_id", table_name="overtime_requests")
    op.drop_table("overtime_requests")
