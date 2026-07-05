from datetime import datetime, UTC
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.news_intelligence.models import NewsArticle, SentimentType


class NewsIntelligenceRepository:
    """Repository to query news articles from the database."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_recent_news(
        self, currency: Optional[str] = None, sentiment: Optional[str] = None, limit: int = 10
    ) -> List[NewsArticle]:
        """Fetch recent news articles ordered by published_at descending."""
        stmt = select(NewsArticle).order_by(NewsArticle.published_at.desc())

        if currency:
            # currency_tags is a comma-separated string; use LIKE for filtering
            stmt = stmt.where(NewsArticle.currency_tags.contains(currency.upper()))

        if sentiment:
            stmt = stmt.where(NewsArticle.sentiment == sentiment.lower())

        stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_bullish_news(self, limit: int = 10) -> List[NewsArticle]:
        """Fetch news articles with bullish sentiment sorted by strongest score."""
        stmt = (
            select(NewsArticle)
            .where(NewsArticle.sentiment == SentimentType.BULLISH)
            .order_by(NewsArticle.sentiment_score.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_bearish_news(self, limit: int = 10) -> List[NewsArticle]:
        """Fetch news articles with bearish sentiment sorted by strongest negative score."""
        stmt = (
            select(NewsArticle)
            .where(NewsArticle.sentiment == SentimentType.BEARISH)
            .order_by(NewsArticle.sentiment_score.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
