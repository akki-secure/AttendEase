"""create account_unlock_logs table

Revision ID: 0017
Revises: 0016
Create Date: 2026-07-19

"""
from alembic import op
import sqlalchemy as sa

revision = "0017"
down_revision = "0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "account_unlock_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("unlocked_by_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("(CURRENT_TIMESTAMP)")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["unlocked_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_account_unlock_logs_user_id", "account_unlock_logs", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_account_unlock_logs_user_id", "account_unlock_logs")
    op.drop_table("account_unlock_logs")
