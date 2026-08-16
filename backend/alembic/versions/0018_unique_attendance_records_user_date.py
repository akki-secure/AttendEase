"""add unique constraint on attendance_records(user_id, date)

Revision ID: 0018
Revises: 0017
Create Date: 2026-08-16

"""
from alembic import op
import sqlalchemy as sa

revision = "0018"
down_revision = "0017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("attendance_records") as batch_op:
        batch_op.create_unique_constraint(
            "uq_attendance_records_user_id_date", ["user_id", "date"]
        )


def downgrade() -> None:
    with op.batch_alter_table("attendance_records") as batch_op:
        batch_op.drop_constraint("uq_attendance_records_user_id_date", type_="unique")
