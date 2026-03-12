"""add education to site registrations

Revision ID: 20260312_0003
Revises: 20260312_0002
Create Date: 2026-03-12 00:20:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260312_0003"
down_revision: Union[str, Sequence[str], None] = "20260312_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("site_registrations", sa.Column("education", sa.String(length=120), nullable=True))


def downgrade() -> None:
    op.drop_column("site_registrations", "education")
