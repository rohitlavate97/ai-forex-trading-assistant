"""create economic events table

Revision ID: d002_create_economic_events_table
Revises: d001_create_users_table
Create Date: 2026-07-05 12:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd002_create_economic_events_table'
down_revision: Union[str, Sequence[str], None] = 'd001_create_users_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema: create economic_events table and corresponding indexes."""
    op.create_table(
        'economic_events',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=False),
        sa.Column('event_name', sa.String(length=150), nullable=False),
        sa.Column('country', sa.String(length=50), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False),
        sa.Column('importance', sa.String(length=20), nullable=False),
        sa.Column('event_time', sa.DateTime(), nullable=False),
        sa.Column('actual', sa.String(length=50), nullable=True),
        sa.Column('forecast', sa.String(length=50), nullable=True),
        sa.Column('previous', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=36), nullable=True),
        sa.Column('updated_by', sa.String(length=36), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_event_uuid', 'economic_events', ['uuid'], unique=True)
    op.create_index('idx_event_country', 'economic_events', ['country'], unique=False)
    op.create_index('idx_event_currency', 'economic_events', ['currency'], unique=False)
    op.create_index('idx_event_importance', 'economic_events', ['importance'], unique=False)
    op.create_index('idx_event_time', 'economic_events', ['event_time'], unique=False)


def downgrade() -> None:
    """Downgrade database schema: drop economic_events table and corresponding indexes."""
    op.drop_index('idx_event_time', table_name='economic_events')
    op.drop_index('idx_event_importance', table_name='economic_events')
    op.drop_index('idx_event_currency', table_name='economic_events')
    op.drop_index('idx_event_country', table_name='economic_events')
    op.drop_index('idx_event_uuid', table_name='economic_events')
    op.drop_table('economic_events')
