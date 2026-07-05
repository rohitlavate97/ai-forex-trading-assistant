"""create news articles table

Revision ID: d003_create_news_articles_table
Revises: d002_create_economic_events_table
Create Date: 2026-07-05 13:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd003_create_news_articles_table'
down_revision: Union[str, Sequence[str], None] = 'd002_create_economic_events_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema: create news_articles table and corresponding indexes."""
    op.create_table(
        'news_articles',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('url', sa.String(length=255), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('summary', sa.String(length=500), nullable=False),
        sa.Column('published_at', sa.DateTime(), nullable=False),
        sa.Column('sentiment', sa.String(length=20), nullable=False),
        sa.Column('sentiment_score', sa.Float(), nullable=False),
        sa.Column('currency_tags', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=36), nullable=True),
        sa.Column('updated_by', sa.String(length=36), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_news_uuid', 'news_articles', ['uuid'], unique=True)
    op.create_index('idx_news_published_at', 'news_articles', ['published_at'], unique=False)
    op.create_index('idx_news_sentiment', 'news_articles', ['sentiment'], unique=False)
    op.create_index('idx_news_currency_tags', 'news_articles', ['currency_tags'], unique=False)


def downgrade() -> None:
    """Downgrade database schema: drop news_articles table and corresponding indexes."""
    op.drop_index('idx_news_currency_tags', table_name='news_articles')
    op.drop_index('idx_news_sentiment', table_name='news_articles')
    op.drop_index('idx_news_published_at', table_name='news_articles')
    op.drop_index('idx_news_uuid', table_name='news_articles')
    op.drop_table('news_articles')
