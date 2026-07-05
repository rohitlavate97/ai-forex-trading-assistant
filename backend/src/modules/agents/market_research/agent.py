from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from src.core.config import settings
from src.modules.agents.market_research.prompts import SYSTEM_PROMPT
from src.modules.agents.market_research.tools import (
    get_currency_overview,
    get_volatility_summary,
    get_trend_summary
)

if settings.OPENAI_API_KEY:
    agent_model = OpenAIChatModel(settings.LLM_MODEL, provider=OpenAIProvider(api_key=settings.OPENAI_API_KEY))
else:
    agent_model = "test"

# Define the Market Research Agent
market_research_agent = Agent(
    model=agent_model,
    system_prompt=SYSTEM_PROMPT,
    retries=2
)

# Register tools
market_research_agent.tool(get_currency_overview)
market_research_agent.tool(get_volatility_summary)
market_research_agent.tool(get_trend_summary)
