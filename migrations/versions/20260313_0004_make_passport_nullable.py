"""make passport nullable in site_registrations

Revision ID: 20260313_0004
Revises: 20260312_0003
Create Date: 2026-03-13 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260313_0004"
down_revision: Union[str, Sequence[str], None] = "20260312_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("site_registrations", "passport", existing_type=sa.Text(), nullable=True)


def downgrade() -> None:
    op.alter_column("site_registrations", "passport", existing_type=sa.Text(), nullable=False)
