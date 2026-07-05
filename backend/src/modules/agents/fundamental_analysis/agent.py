from typing import Optional
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.modules.agents.fundamental_analysis.prompts import SYSTEM_PROMPT
from src.modules.agents.fundamental_analysis.tools import (
    get_macroeconomic_data,
    get_news_sentiment_data
)

if settings.OPENAI_API_KEY:
    agent_model = OpenAIChatModel(settings.LLM_MODEL, provider=OpenAIProvider(api_key=settings.OPENAI_API_KEY))
else:
    agent_model = "test"

# Define the Fundamental Analysis Agent
fundamental_analysis_agent = Agent(
    model=agent_model,
    system_prompt=SYSTEM_PROMPT,
    deps_type=AsyncSession,
    retries=2
)

# Register tools
fundamental_analysis_agent.tool(get_macroeconomic_data)
fundamental_analysis_agent.tool(get_news_sentiment_data)
