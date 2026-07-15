"""create geofence_settings table

Revision ID: 0015
Revises: 0014
Create Date: 2026-07-15

"""
from alembic import op
import sqlalchemy as sa

revision = "0015"
down_revision = "0014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "geofence_settings",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.execute("INSERT INTO geofence_settings (id, enabled) VALUES (1, false)")


def downgrade() -> None:
    op.drop_table("geofence_settings")
