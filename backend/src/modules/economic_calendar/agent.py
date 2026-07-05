from typing import Optional, List
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.config import settings
from src.modules.economic_calendar.prompts import SYSTEM_PROMPT
from src.modules.economic_calendar.service import EconomicCalendarService
from src.modules.economic_calendar.schemas import EconomicEventResponse

if settings.OPENAI_API_KEY:
    agent_model = OpenAIChatModel(settings.LLM_MODEL, provider=OpenAIProvider(api_key=settings.OPENAI_API_KEY))
else:
    agent_model = "test"

# Declare the Economic Calendar Specialist Agent
# It expects an AsyncSession as its context dependency (deps)
economic_calendar_agent = Agent(
    agent_model,
    deps_type=AsyncSession,
    system_prompt=SYSTEM_PROMPT,
)


@economic_calendar_agent.tool
async def get_upcoming_events(
    ctx: RunContext[AsyncSession], currency: Optional[str] = None, limit: int = 10
) -> List[dict]:
    """
    Retrieve upcoming high/medium/low impact macroeconomic events from the database.
    Optional 'currency' (e.g. 'USD', 'EUR') filters events.
    """
    service = EconomicCalendarService(ctx.deps)
    results = await service.get_upcoming(currency=currency, limit=limit)
    return [r.model_dump() for r in results]


@economic_calendar_agent.tool
async def get_recent_events(
    ctx: RunContext[AsyncSession], currency: Optional[str] = None, limit: int = 10
) -> List[dict]:
    """
    Retrieve past macroeconomic events (featuring actual vs forecast vs previous results).
    Optional 'currency' (e.g. 'USD', 'EUR') filters events.
    """
    service = EconomicCalendarService(ctx.deps)
    results = await service.get_recent(currency=currency, limit=limit)
    return [r.model_dump() for r in results]


@economic_calendar_agent.tool
async def get_high_impact_events(
    ctx: RunContext[AsyncSession], limit: int = 10
) -> List[dict]:
    """
    Retrieve high impact macroeconomic events from the database.
    """
    service = EconomicCalendarService(ctx.deps)
    results = await service.get_high_impact(limit=limit)
    return [r.model_dump() for r in results]
