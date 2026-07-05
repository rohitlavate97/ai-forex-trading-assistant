from typing import Any
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from src.core.config import settings
from src.modules.agents.tech_analysis.prompts import SYSTEM_PROMPT
from src.modules.agents.tech_analysis.tools import (
    tool_get_indicators_summary,
    tool_get_advanced_indicators,
)

# Initialize OpenAI Model using credentials from global Settings
# If the key is blank, we can create a dummy model to prevent startup crashes
if settings.OPENAI_API_KEY:
    agent_model = OpenAIChatModel(settings.LLM_MODEL, provider=OpenAIProvider(api_key=settings.OPENAI_API_KEY))
else:
    # Fallback to a placeholder model that can be overridden in tests
    agent_model = "test"

# Declare the Technical Analysis Specialist Agent
tech_analysis_agent = Agent(
    agent_model,
    system_prompt=SYSTEM_PROMPT,
)


@tech_analysis_agent.tool
async def get_indicators_summary(ctx: RunContext[None], symbol: str) -> dict:
    """
    Query and calculate standard technical indicators (RSI, MACD, Bollinger Bands)
    for a given currency pair symbol (e.g. 'EUR/USD').
    """
    return await tool_get_indicators_summary(symbol)


@tech_analysis_agent.tool
async def get_advanced_indicators(ctx: RunContext[None], symbol: str) -> dict:
    """
    Query and calculate advanced technical indicators (ATR, Fibonacci Retracement, Ichimoku Cloud)
    for a given currency pair symbol (e.g. 'EUR/USD').
    """
    return await tool_get_advanced_indicators(symbol)
