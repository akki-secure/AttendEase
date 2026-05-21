"""create attendance_records table

Revision ID: 0003
Revises: 0002
Create Date: 2026-05-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "attendance_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("clock_in", sa.DateTime(), nullable=True),
        sa.Column("clock_out", sa.DateTime(), nullable=True),
        sa.Column("break_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="PRESENT"),
        sa.Column("correction_note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("(CURRENT_TIMESTAMP)")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("(CURRENT_TIMESTAMP)")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_attendance_records_user_id", "attendance_records", ["user_id"])
    op.create_index("ix_attendance_records_date", "attendance_records", ["date"])


def downgrade() -> None:
    op.drop_index("ix_attendance_records_date", "attendance_records")
    op.drop_index("ix_attendance_records_user_id", "attendance_records")
    op.drop_table("attendance_records")
