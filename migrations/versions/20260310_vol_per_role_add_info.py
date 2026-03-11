"""bridge missing historical revision

Revision ID: 20260310_vol_per_role_add_info
Revises:
Create Date: 2026-03-10 00:00:00.000000
"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "20260310_vol_per_role_add_info"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # This migration is a compatibility bridge for an existing DB stamp.
    pass


def downgrade() -> None:
    pass
