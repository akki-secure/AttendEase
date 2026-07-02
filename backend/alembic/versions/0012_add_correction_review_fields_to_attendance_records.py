"""add correction review fields to attendance_records

Revision ID: 0012
Revises: 0011
Create Date: 2026-07-01

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0012"
down_revision: Union[str, None] = "0011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("attendance_records", sa.Column("original_clock_in", sa.DateTime(), nullable=True))
    op.add_column("attendance_records", sa.Column("original_clock_out", sa.DateTime(), nullable=True))
    op.add_column("attendance_records", sa.Column("original_break_minutes", sa.Integer(), nullable=True))
    op.add_column("attendance_records", sa.Column("original_status", sa.String(length=30), nullable=True))
    op.add_column("attendance_records", sa.Column("reviewer_id", sa.Integer(), nullable=True))
    op.add_column("attendance_records", sa.Column("reviewer_comment", sa.Text(), nullable=True))
    op.add_column("attendance_records", sa.Column("reviewed_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("attendance_records", "reviewed_at")
    op.drop_column("attendance_records", "reviewer_comment")
    op.drop_column("attendance_records", "reviewer_id")
    op.drop_column("attendance_records", "original_status")
    op.drop_column("attendance_records", "original_break_minutes")
    op.drop_column("attendance_records", "original_clock_out")
    op.drop_column("attendance_records", "original_clock_in")
