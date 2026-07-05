"""create users table

Revision ID: d001_create_users_table
Revises: 
Create Date: 2026-07-05 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd001_create_users_table'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema: create users table and corresponding indexes."""
    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=36), nullable=True),
        sa.Column('updated_by', sa.String(length=36), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_user_uuid', 'users', ['uuid'], unique=True)
    op.create_index('idx_user_username', 'users', ['username'], unique=True)
    op.create_index('idx_user_email', 'users', ['email'], unique=True)
    op.create_index('idx_user_role', 'users', ['role'], unique=False)


def downgrade() -> None:
    """Downgrade database schema: drop users table and corresponding indexes."""
    op.drop_index('idx_user_role', table_name='users')
    op.drop_index('idx_user_email', table_name='users')
    op.drop_index('idx_user_username', table_name='users')
    op.drop_index('idx_user_uuid', table_name='users')
    op.drop_table('users')
