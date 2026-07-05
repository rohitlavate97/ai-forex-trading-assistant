from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.economic_calendar.repository import EconomicCalendarRepository
from src.modules.economic_calendar.schemas import EconomicEventResponse


class EconomicCalendarService:
    """Service coordinates economic calendar queries."""

    def __init__(self, db: AsyncSession) -> None:
        self.repo = EconomicCalendarRepository(db)

    async def get_upcoming(self, currency: Optional[str] = None, limit: int = 10) -> List[EconomicEventResponse]:
        events = await self.repo.get_upcoming_events(currency, limit)
        return [EconomicEventResponse.model_validate(e) for e in events]

    async def get_recent(self, currency: Optional[str] = None, limit: int = 10) -> List[EconomicEventResponse]:
        events = await self.repo.get_recent_events(currency, limit)
        return [EconomicEventResponse.model_validate(e) for e in events]

    async def get_high_impact(self, limit: int = 10) -> List[EconomicEventResponse]:
        events = await self.repo.get_high_impact_events(limit)
        return [EconomicEventResponse.model_validate(e) for e in events]
