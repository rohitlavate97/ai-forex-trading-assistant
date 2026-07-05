from typing import Optional, List
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.config import settings
from src.modules.news_intelligence.prompts import SYSTEM_PROMPT
from src.modules.news_intelligence.service import NewsIntelligenceService

if settings.OPENAI_API_KEY:
    agent_model = OpenAIChatModel(settings.LLM_MODEL, provider=OpenAIProvider(api_key=settings.OPENAI_API_KEY))
else:
    agent_model = "test"

# Declare the News Intelligence Specialist Agent
# It expects an AsyncSession as its context dependency (deps)
news_intelligence_agent = Agent(
    agent_model,
    deps_type=AsyncSession,
    system_prompt=SYSTEM_PROMPT,
)


@news_intelligence_agent.tool
async def get_recent_news(
    ctx: RunContext[AsyncSession],
    currency: Optional[str] = None,
    sentiment: Optional[str] = None,
    limit: int = 10,
) -> List[dict]:
    """
    Retrieve recent forex-related news articles from the database.
    Optional 'currency' (e.g. 'USD', 'EUR') and 'sentiment' (bullish, bearish, neutral) filters.
    """
    service = NewsIntelligenceService(ctx.deps)
    results = await service.get_recent(currency=currency, sentiment=sentiment, limit=limit)
    return [r.model_dump() for r in results]


@news_intelligence_agent.tool
async def get_bullish_news(ctx: RunContext[AsyncSession], limit: int = 10) -> List[dict]:
    """
    Retrieve news articles with bullish sentiment sorted by strongest positive score.
    """
    service = NewsIntelligenceService(ctx.deps)
    results = await service.get_bullish(limit=limit)
    return [r.model_dump() for r in results]


@news_intelligence_agent.tool
async def get_bearish_news(ctx: RunContext[AsyncSession], limit: int = 10) -> List[dict]:
    """
    Retrieve news articles with bearish sentiment sorted by strongest negative score.
    """
    service = NewsIntelligenceService(ctx.deps)
    results = await service.get_bearish(limit=limit)
    return [r.model_dump() for r in results]
