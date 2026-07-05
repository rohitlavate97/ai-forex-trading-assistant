from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic_ai import RunContext

from src.modules.economic_calendar.repository import EconomicCalendarRepository
from src.modules.news_intelligence.repository import NewsIntelligenceRepository


async def get_macroeconomic_data(
    ctx: RunContext[AsyncSession], currency: str, limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Fetch recent high-impact macroeconomic events for a specific currency.
    Useful for understanding central bank policies, inflation, and employment data.

    Args:
        ctx: RunContext containing the database session.
        currency: The 3-letter currency code (e.g., "USD", "EUR").
        limit: Maximum number of recent events to retrieve.
    """
    session = ctx.deps
    repo = EconomicCalendarRepository(session)
    # Get upcoming/recent events filtered by currency and High impact
    events = await repo.get_events(currency=currency, impact="High", limit=limit)
    
    return [
        {
            "event_name": event.event_name,
            "currency": event.currency,
            "impact": event.impact,
            "actual": event.actual,
            "forecast": event.forecast,
            "previous": event.previous,
            "time": event.event_time.isoformat() if event.event_time else None
        }
        for event in events
    ]


async def get_news_sentiment_data(
    ctx: RunContext[AsyncSession], currency: str, limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Fetch recent news articles and their sentiment scores for a specific currency.
    Useful for understanding the current qualitative market mood.

    Args:
        ctx: RunContext containing the database session.
        currency: The 3-letter currency code (e.g., "USD", "EUR").
        limit: Maximum number of recent articles to retrieve.
    """
    session = ctx.deps
    repo = NewsIntelligenceRepository(session)
    # Fetch recent news for the currency
    articles = await repo.get_recent_news(currency=currency, limit=limit)
    
    return [
        {
            "title": article.title,
            "source": article.source,
            "sentiment": article.sentiment,
            "sentiment_score": article.sentiment_score,
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "summary": article.summary
        }
        for article in articles
    ]
