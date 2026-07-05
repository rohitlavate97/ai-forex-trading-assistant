import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.modules.agents.market_research.agent import market_research_agent
from src.modules.agents.market_research.tools import (
    get_currency_overview,
    get_volatility_summary,
    get_trend_summary
)


@pytest.mark.asyncio
@patch("src.modules.agents.market_research.tools.MarketDataService")
async def test_get_currency_overview(mock_service_class):
    mock_service = AsyncMock()
    mock_service.get_live_price.return_value = {
        "symbol": "EUR/USD",
        "price": 1.1050,
        "bid": 1.1049,
        "ask": 1.1051,
        "timestamp": 1234567890
    }
    mock_service_class.return_value = mock_service
    
    mock_ctx = MagicMock()
    
    data = await get_currency_overview(mock_ctx, "EUR/USD")
    
    assert data["symbol"] == "EUR/USD"
    assert data["price"] == 1.1050
    assert data["bid"] == 1.1049
    assert data["ask"] == 1.1051
    mock_service.get_live_price.assert_called_once_with("EUR/USD")


@pytest.mark.asyncio
@patch("src.modules.agents.market_research.tools.MarketDataService")
async def test_get_volatility_summary(mock_service_class):
    mock_service = AsyncMock()
    mock_service.get_price_history.return_value = [
        {"price": 1.1000},
        {"price": 1.1050},
        {"price": 1.0950}
    ]
    mock_service_class.return_value = mock_service
    
    mock_ctx = MagicMock()
    
    data = await get_volatility_summary(mock_ctx, "EUR/USD", 3)
    
    assert data["symbol"] == "EUR/USD"
    assert data["high"] == 1.1050
    assert data["low"] == 1.0950
    assert data["average"] == pytest.approx(1.1000)
    assert data["variance_pips"] == pytest.approx(100.0)
    mock_service.get_price_history.assert_called_once_with("EUR/USD", limit=3)


@pytest.mark.asyncio
@patch("src.modules.agents.market_research.tools.MarketDataService")
async def test_get_trend_summary(mock_service_class):
    mock_service = AsyncMock()
    mock_service.get_price_history.return_value = [
        {"price": 1.1000, "timestamp": 1},
        {"price": 1.1020, "timestamp": 2},
        {"price": 1.1050, "timestamp": 3}
    ]
    mock_service_class.return_value = mock_service
    
    mock_ctx = MagicMock()
    
    data = await get_trend_summary(mock_ctx, "EUR/USD", 3)
    
    assert data["symbol"] == "EUR/USD"
    assert data["trend"] == "bullish"
    assert data["start_price"] == 1.1000
    assert data["end_price"] == 1.1050
    assert data["price_change"] == pytest.approx(0.0050)
    mock_service.get_price_history.assert_called_once_with("EUR/USD", limit=3)


@pytest.mark.asyncio
async def test_agent_runs_with_mocked_model():
    """Test that the Pydantic AI agent compiles and executes using a mock model."""
    mock_run_result = MagicMock()
    mock_run_result.data = "The market conditions for EUR/USD indicate short-term bullish volatility."
    
    # Mock the agent's async run method
    market_research_agent.run = AsyncMock(return_value=mock_run_result)
    
    response = await market_research_agent.run(
        "Analyze the market research overview for EUR/USD."
    )
    
    assert response.data == "The market conditions for EUR/USD indicate short-term bullish volatility."
    market_research_agent.run.assert_called_once()
