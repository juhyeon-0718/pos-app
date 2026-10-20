"""add menus.deleted_at for soft delete (B-12, D-37)

Revision ID: a3d9b12e5c40
Revises: 337a1c1c7083
Create Date: 2026-10-20 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3d9b12e5c40'
down_revision: Union[str, Sequence[str], None] = '337a1c1c7083'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('menus', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('menus', 'deleted_at')
