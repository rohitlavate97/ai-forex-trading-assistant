from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.modules.news_intelligence.schemas import NewsArticleResponse
from src.modules.news_intelligence.service import NewsIntelligenceService

router = APIRouter(prefix="/news", tags=["News Intelligence"])


@router.get("/recent", response_model=List[NewsArticleResponse])
async def get_recent_news(
    currency: Optional[str] = Query(None, description="Filter by currency tag (e.g. USD, EUR)"),
    sentiment: Optional[str] = Query(None, description="Filter by sentiment (bullish, bearish, neutral)"),
    limit: int = Query(10, ge=1, le=50, description="Number of articles to retrieve"),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve recent forex-related news articles with optional sentiment and currency filters."""
    service = NewsIntelligenceService(db)
    return await service.get_recent(currency=currency, sentiment=sentiment, limit=limit)


@router.get("/bullish", response_model=List[NewsArticleResponse])
async def get_bullish_news(
    limit: int = Query(10, ge=1, le=50, description="Number of articles to retrieve"),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve news articles with bullish sentiment sorted by strongest positive score."""
    service = NewsIntelligenceService(db)
    return await service.get_bullish(limit=limit)


@router.get("/bearish", response_model=List[NewsArticleResponse])
async def get_bearish_news(
    limit: int = Query(10, ge=1, le=50, description="Number of articles to retrieve"),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve news articles with bearish sentiment sorted by strongest negative score."""
    service = NewsIntelligenceService(db)
    return await service.get_bearish(limit=limit)
