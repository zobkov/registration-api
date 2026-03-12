"""add numeric key to site registrations

Revision ID: 20260312_0002
Revises: 20260312_0001
Create Date: 2026-03-12 00:10:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260312_0002"
down_revision: Union[str, Sequence[str], None] = "20260312_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Keep nullable for existing rows; new rows receive generated values in application code.
    op.add_column("site_registrations", sa.Column("numeric_key", sa.String(length=6), nullable=True))
    op.create_unique_constraint(
        "uq_site_registrations_numeric_key", "site_registrations", ["numeric_key"]
    )
    op.create_index("ix_site_registrations_numeric_key", "site_registrations", ["numeric_key"])


def downgrade() -> None:
    op.drop_index("ix_site_registrations_numeric_key", table_name="site_registrations")
    op.drop_constraint("uq_site_registrations_numeric_key", "site_registrations", type_="unique")
    op.drop_column("site_registrations", "numeric_key")
