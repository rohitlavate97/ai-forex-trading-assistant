from typing import List, Dict, Any
from pydantic_ai import RunContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.rag.service import RAGService
from src.modules.agents.market_research.tools import get_currency_overview
from src.modules.agents.fundamental_analysis.tools import get_news_sentiment_data, get_macroeconomic_data


async def search_knowledge_base(
    ctx: RunContext[AsyncSession], query: str, limit: int = 3
) -> List[Dict[str, Any]]:
    """
    Search the RAG Knowledge Base for documents uploaded by the user matching the query.
    Always cite the filename in your response if you use this information.

    Args:
        ctx: RunContext
        query: The search string.
        limit: Max results to return.
    """
    service = RAGService()
    results = await service.query_knowledge_base(query, limit)
    return results


async def get_live_market_overview(
    ctx: RunContext[AsyncSession], symbol: str
) -> Dict[str, Any]:
    """
    Fetch the current live price overview for a currency pair, including bid and ask.

    Args:
        ctx: RunContext
        symbol: Currency pair symbol (e.g., "EUR/USD").
    """
    # The market overview tool requires RunContext[None], but we can pass it our RunContext
    # since it ignores the dependency anyway.
    return await get_currency_overview(ctx, symbol)


async def get_recent_news_sentiment(
    ctx: RunContext[AsyncSession], currency: str, limit: int = 3
) -> List[Dict[str, Any]]:
    """
    Fetch recent news articles and their sentiment scores for a specific currency.

    Args:
        ctx: RunContext containing the database session.
        currency: The 3-letter currency code (e.g., "USD", "EUR").
        limit: Max articles.
    """
    return await get_news_sentiment_data(ctx, currency, limit)


async def get_recent_macroeconomic_events(
    ctx: RunContext[AsyncSession], currency: str, limit: int = 3
) -> List[Dict[str, Any]]:
    """
    Fetch recent high-impact macroeconomic events for a specific currency.

    Args:
        ctx: RunContext containing the database session.
        currency: The 3-letter currency code (e.g., "USD", "EUR").
        limit: Max events.
    """
    return await get_macroeconomic_data(ctx, currency, limit)
