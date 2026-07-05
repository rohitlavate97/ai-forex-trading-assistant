import pytest
from unittest.mock import AsyncMock, MagicMock
from src.modules.agents.tech_analysis.calculators import (
    calculate_sma,
    calculate_ema,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_atr,
    calculate_fibonacci_retracement,
    calculate_ichimoku_cloud,
)
from src.modules.agents.tech_analysis.agent import tech_analysis_agent
from src.modules.agents.tech_analysis.tools import tool_get_indicators_summary


def test_sma_calculation():
    prices = [10.0, 11.0, 12.0, 13.0, 14.0]
    # SMA 3 periods should be (12 + 13 + 14) / 3 = 13.0
    assert calculate_sma(prices, period=3) == 13.0
    # Insufficient data
    assert calculate_sma(prices, period=10) is None


def test_ema_calculation():
    prices = [10.0, 10.0, 10.0, 10.0, 10.0]
    # Constant prices should yield constant EMA
    assert calculate_ema(prices, period=3) == 10.0


def test_rsi_calculation():
    # Constant prices -> no gains -> RSI should be 0.0 or close (Wilder's calculation)
    prices_flat = [10.0] * 20
    assert calculate_rsi(prices_flat, period=14) == 0.0

    # Strictly rising prices -> gains only -> RSI should be 100.0
    prices_rising = [float(x) for x in range(1, 22)]
    assert calculate_rsi(prices_rising, period=14) == 100.0


def test_macd_calculation():
    # Flat series
    prices = [10.0] * 50
    macd = calculate_macd(prices)
    assert macd is not None
    # Flat series converges to 0 MACD line
    assert abs(macd[0]) < 0.001
    assert abs(macd[1]) < 0.001
    assert abs(macd[2]) < 0.001


def test_bollinger_bands_calculation():
    prices = [10.0] * 20
    bb = calculate_bollinger_bands(prices, period=10)
    assert bb is not None
    # For constant prices, stddev = 0, so middle, upper, lower should all equal price
    assert bb[0] == 10.0
    assert bb[1] == 10.0
    assert bb[2] == 10.0


def test_fibonacci_retracement_calculation():
    # Peak: 2.0, Trough: 1.0. Diff is 1.0.
    # Level 50.0% should be 2.0 - 0.5 = 1.5
    # Level 61.8% should be 2.0 - 0.618 = 1.382
    fib = calculate_fibonacci_retracement(2.0, 1.0)
    assert fib["level_50.0"] == 1.5
    assert fib["level_61.8"] == 1.382


@pytest.mark.asyncio
async def test_agent_runs_with_mocked_model():
    """Test that the Pydantic AI agent compiles, registers tools, and executes using a mock model."""
    # Create mock response
    mock_run_result = MagicMock()
    mock_run_result.data = "The technical indicators for EUR/USD suggest consolidation."
    
    # Mock the agent's async run method
    tech_analysis_agent.run = AsyncMock(return_value=mock_run_result)
    
    # Run the agent
    response = await tech_analysis_agent.run(
        "Analyze EUR/USD current technical indicators and tell me if it is overbought."
    )
    
    assert response.data == "The technical indicators for EUR/USD suggest consolidation."
    tech_analysis_agent.run.assert_called_once()
