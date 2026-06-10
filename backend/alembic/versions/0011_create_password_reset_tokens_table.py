"""create password_reset_tokens table

Revision ID: 0011
Revises: 0010
Create Date: 2026-06-06

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0011"
down_revision: Union[str, None] = "0010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("employee_id", sa.String(50), nullable=False),
        sa.Column("code", sa.String(255), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("used", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("(CURRENT_TIMESTAMP)")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_password_reset_tokens_employee_id", "password_reset_tokens", ["employee_id"])
    op.create_index(
        "uq_password_reset_tokens_active",
        "password_reset_tokens",
        ["employee_id"],
        unique=True,
        postgresql_where="used = false",
        sqlite_where="used = 0",
    )


def downgrade() -> None:
    op.drop_index("uq_password_reset_tokens_active", table_name="password_reset_tokens")
    op.drop_index("ix_password_reset_tokens_employee_id", table_name="password_reset_tokens")
    op.drop_table("password_reset_tokens")
