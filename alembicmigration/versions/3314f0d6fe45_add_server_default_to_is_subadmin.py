"""add server default to is_subadmin

Revision ID: 3314f0d6fe45
Revises: f11e750af24b
Create Date: 2026-03-02 21:47:39.623844

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3314f0d6fe45'
down_revision: Union[str, Sequence[str], None] = 'f11e750af24b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('admins', 'is_subadmin',
                    existing_type=sa.Boolean(),
                    server_default='1',
                    existing_nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('admins', 'is_subadmin',
                    existing_type=sa.Boolean(),
                    server_default=None,
                    existing_nullable=True)
