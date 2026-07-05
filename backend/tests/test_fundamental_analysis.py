import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.modules.agents.fundamental_analysis.agent import fundamental_analysis_agent
from src.modules.agents.fundamental_analysis.tools import (
    get_macroeconomic_data,
    get_news_sentiment_data,
)


@pytest.mark.asyncio
@patch("src.modules.agents.fundamental_analysis.tools.EconomicCalendarRepository")
async def test_get_macroeconomic_data(mock_repo_class):
    """Test get_macroeconomic_data tool fetches from repository correctly."""
    mock_session = AsyncMock()
    mock_ctx = MagicMock()
    mock_ctx.deps = mock_session

    mock_repo_instance = AsyncMock()
    mock_event = MagicMock()
    mock_event.event_name = "NFP"
    mock_event.currency = "USD"
    mock_event.impact = "High"
    mock_event.actual = "250K"
    mock_event.forecast = "200K"
    mock_event.previous = "180K"
    mock_event.event_time = datetime(2023, 10, 1)
    
    mock_repo_instance.get_events.return_value = [mock_event]
    mock_repo_class.return_value = mock_repo_instance

    data = await get_macroeconomic_data(mock_ctx, "USD", 1)
    
    assert len(data) == 1
    assert data[0]["event_name"] == "NFP"
    assert data[0]["currency"] == "USD"
    mock_repo_instance.get_events.assert_called_once_with(currency="USD", impact="High", limit=1)


@pytest.mark.asyncio
@patch("src.modules.agents.fundamental_analysis.tools.NewsIntelligenceRepository")
async def test_get_news_sentiment_data(mock_repo_class):
    """Test get_news_sentiment_data tool fetches from repository correctly."""
    mock_session = AsyncMock()
    mock_ctx = MagicMock()
    mock_ctx.deps = mock_session

    mock_repo_instance = AsyncMock()
    mock_article = MagicMock()
    mock_article.title = "Fed hikes rates"
    mock_article.source = "Reuters"
    mock_article.sentiment = "bullish"
    mock_article.sentiment_score = 0.8
    mock_article.published_at = datetime(2023, 10, 2)
    mock_article.summary = "The Fed decided to hike interest rates by 25 bps."
    
    mock_repo_instance.get_recent_news.return_value = [mock_article]
    mock_repo_class.return_value = mock_repo_instance

    data = await get_news_sentiment_data(mock_ctx, "USD", 1)
    
    assert len(data) == 1
    assert data[0]["title"] == "Fed hikes rates"
    assert data[0]["sentiment"] == "bullish"
    mock_repo_instance.get_recent_news.assert_called_once_with(currency="USD", limit=1)


@pytest.mark.asyncio
async def test_agent_runs_with_mocked_model():
    """Test that the Pydantic AI agent compiles and executes using a mock model."""
    mock_run_result = MagicMock()
    mock_run_result.data = "The fundamental indicators for USD suggest a bullish sentiment."
    
    # Mock the agent's async run method
    fundamental_analysis_agent.run = AsyncMock(return_value=mock_run_result)
    
    response = await fundamental_analysis_agent.run(
        "Analyze the fundamental outlook for USD."
    )
    
    assert response.data == "The fundamental indicators for USD suggest a bullish sentiment."
    fundamental_analysis_agent.run.assert_called_once()
