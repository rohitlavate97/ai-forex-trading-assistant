from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.modules.chat.prompts import SYSTEM_PROMPT
from src.modules.chat.tools import (
    search_knowledge_base,
    get_live_market_overview,
    get_recent_news_sentiment,
    get_recent_macroeconomic_events
)

if settings.OPENAI_API_KEY:
    agent_model = OpenAIChatModel(settings.LLM_MODEL, provider=OpenAIProvider(api_key=settings.OPENAI_API_KEY))
else:
    agent_model = "test"

# Define the Chat Agent
chat_agent = Agent(
    model=agent_model,
    system_prompt=SYSTEM_PROMPT,
    deps_type=AsyncSession,
    retries=2
)

# Register tools
chat_agent.tool(search_knowledge_base)
chat_agent.tool(get_live_market_overview)
chat_agent.tool(get_recent_news_sentiment)
chat_agent.tool(get_recent_macroeconomic_events)
