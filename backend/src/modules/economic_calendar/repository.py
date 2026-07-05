from datetime import datetime, UTC
from typing import List, Optional
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.economic_calendar.models import EconomicEvent, EventImportance


class EconomicCalendarRepository:
    """Repository to query economic events from the database."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_upcoming_events(self, currency: Optional[str] = None, limit: int = 10) -> List[EconomicEvent]:
        """Fetch upcoming economic events relative to current UTC time."""
        now = datetime.now(UTC).replace(tzinfo=None)
        stmt = select(EconomicEvent).where(EconomicEvent.event_time >= now)
        
        if currency:
            stmt = stmt.where(EconomicEvent.currency == currency.upper())
            
        stmt = stmt.order_by(EconomicEvent.event_time.asc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_recent_events(self, currency: Optional[str] = None, limit: int = 10) -> List[EconomicEvent]:
        """Fetch past economic events relative to current UTC time."""
        now = datetime.now(UTC).replace(tzinfo=None)
        stmt = select(EconomicEvent).where(EconomicEvent.event_time < now)
        
        if currency:
            stmt = stmt.where(EconomicEvent.currency == currency.upper())
            
        stmt = stmt.order_by(EconomicEvent.event_time.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_high_impact_events(self, limit: int = 10) -> List[EconomicEvent]:
        """Fetch upcoming or recent high importance economic events."""
        stmt = select(EconomicEvent).where(EconomicEvent.importance == EventImportance.HIGH)
        stmt = stmt.order_by(EconomicEvent.event_time.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
