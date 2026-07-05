from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.news_intelligence.repository import NewsIntelligenceRepository
from src.modules.news_intelligence.schemas import NewsArticleResponse


class NewsIntelligenceService:
    """Service coordinates news intelligence queries."""

    def __init__(self, db: AsyncSession) -> None:
        self.repo = NewsIntelligenceRepository(db)

    async def get_recent(
        self, currency: Optional[str] = None, sentiment: Optional[str] = None, limit: int = 10
    ) -> List[NewsArticleResponse]:
        articles = await self.repo.get_recent_news(currency, sentiment, limit)
        return [NewsArticleResponse.model_validate(a) for a in articles]

    async def get_bullish(self, limit: int = 10) -> List[NewsArticleResponse]:
        articles = await self.repo.get_bullish_news(limit)
        return [NewsArticleResponse.model_validate(a) for a in articles]

    async def get_bearish(self, limit: int = 10) -> List[NewsArticleResponse]:
        articles = await self.repo.get_bearish_news(limit)
        return [NewsArticleResponse.model_validate(a) for a in articles]
