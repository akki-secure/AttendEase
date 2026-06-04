"""add work_type to attendance_records

Revision ID: 0010
Revises: 0009
Create Date: 2026-06-04
"""
from alembic import op
import sqlalchemy as sa

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "attendance_records",
        sa.Column("work_type", sa.String(10), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("attendance_records", "work_type")
