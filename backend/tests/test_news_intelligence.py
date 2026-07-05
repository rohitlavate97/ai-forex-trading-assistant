import pytest
from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.news_intelligence.models import NewsArticle, SentimentType
from src.modules.news_intelligence.repository import NewsIntelligenceRepository
from src.modules.news_intelligence.agent import news_intelligence_agent


@pytest.mark.asyncio
async def test_repository_get_recent_news():
    """Test repository fetches recent news articles with optional filters."""
    mock_session = AsyncMock(spec=AsyncSession)

    article = NewsArticle(
        title="Fed Signals Potential Rate Hold in September",
        source="Reuters",
        summary="Federal Reserve officials indicated rates may hold steady.",
        published_at=datetime(2026, 7, 4, 14, 0, 0),
        sentiment=SentimentType.NEUTRAL,
        sentiment_score=0.05,
        currency_tags="USD",
    )

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [article]
    mock_session.execute = AsyncMock(return_value=mock_result)

    repo = NewsIntelligenceRepository(mock_session)
    articles = await repo.get_recent_news(currency="USD", limit=5)

    assert len(articles) == 1
    assert articles[0].title == "Fed Signals Potential Rate Hold in September"
    assert articles[0].sentiment == SentimentType.NEUTRAL
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_repository_get_bullish_news():
    """Test repository returns bullish news sorted by strongest score."""
    mock_session = AsyncMock(spec=AsyncSession)

    article = NewsArticle(
        title="EUR Rally Accelerates on ECB Hawkish Signals",
        source="Bloomberg",
        summary="Euro strengthened significantly after hawkish ECB commentary.",
        published_at=datetime(2026, 7, 3, 10, 0, 0),
        sentiment=SentimentType.BULLISH,
        sentiment_score=0.85,
        currency_tags="EUR",
    )

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [article]
    mock_session.execute = AsyncMock(return_value=mock_result)

    repo = NewsIntelligenceRepository(mock_session)
    articles = await repo.get_bullish_news(limit=3)

    assert len(articles) == 1
    assert articles[0].sentiment == SentimentType.BULLISH
    assert articles[0].sentiment_score == 0.85


@pytest.mark.asyncio
async def test_repository_get_bearish_news():
    """Test repository returns bearish news sorted by most negative score."""
    mock_session = AsyncMock(spec=AsyncSession)

    article = NewsArticle(
        title="GBP Drops on Weak UK Economic Outlook",
        source="Financial Times",
        summary="Sterling fell as growth forecasts were revised downward.",
        published_at=datetime(2026, 7, 2, 8, 0, 0),
        sentiment=SentimentType.BEARISH,
        sentiment_score=-0.72,
        currency_tags="GBP",
    )

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [article]
    mock_session.execute = AsyncMock(return_value=mock_result)

    repo = NewsIntelligenceRepository(mock_session)
    articles = await repo.get_bearish_news(limit=3)

    assert len(articles) == 1
    assert articles[0].sentiment == SentimentType.BEARISH
    assert articles[0].sentiment_score == -0.72


@pytest.mark.asyncio
async def test_news_intelligence_agent_tool_binding():
    """Test that news intelligence agent compiles and executes using dependency injection."""
    mock_run_result = MagicMock()
    mock_run_result.data = "Recent news sentiment for USD is predominantly neutral with a slight bullish bias."

    news_intelligence_agent.run = AsyncMock(return_value=mock_run_result)
    mock_session = AsyncMock(spec=AsyncSession)

    response = await news_intelligence_agent.run(
        "What is the current news sentiment for USD?",
        deps=mock_session,
    )

    assert response.data == "Recent news sentiment for USD is predominantly neutral with a slight bullish bias."
    news_intelligence_agent.run.assert_called_once_with(
        "What is the current news sentiment for USD?",
        deps=mock_session,
    )
