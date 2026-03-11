"""create site registrations table

Revision ID: 20260312_0001
Revises:
Create Date: 2026-03-12 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260312_0001"
down_revision: Union[str, Sequence[str], None] = "20260310_vol_per_role_add_info"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "site_registrations",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("adult18", sa.String(length=3), nullable=True),
        sa.Column("region", sa.String(length=120), nullable=True),
        sa.Column("participant_status", sa.String(length=64), nullable=True),
        sa.Column("track", sa.String(length=32), nullable=True),
        sa.Column("transport", sa.String(length=64), nullable=False),
        sa.Column("car_number", sa.String(length=24), nullable=True),
        sa.Column("passport", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("email", name="uq_site_registrations_email"),
    )
    op.create_index("ix_site_registrations_created_at", "site_registrations", ["created_at"])
    op.create_index("ix_site_registrations_status", "site_registrations", ["status"])
    op.create_index("ix_site_registrations_email", "site_registrations", ["email"])


def downgrade() -> None:
    op.drop_index("ix_site_registrations_email", table_name="site_registrations")
    op.drop_index("ix_site_registrations_status", table_name="site_registrations")
    op.drop_index("ix_site_registrations_created_at", table_name="site_registrations")
    op.drop_table("site_registrations")
