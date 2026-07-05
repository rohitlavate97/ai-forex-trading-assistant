from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.modules.economic_calendar.schemas import EconomicEventResponse
from src.modules.economic_calendar.service import EconomicCalendarService

router = APIRouter(prefix="/economic-calendar", tags=["Economic Calendar"])


@router.get("/upcoming", response_model=List[EconomicEventResponse])
async def get_upcoming_events(
    currency: Optional[str] = Query(None, description="Filter by currency code (e.g. USD, EUR)"),
    limit: int = Query(10, ge=1, le=50, description="Number of events to retrieve"),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve upcoming high/medium/low impact macroeconomic events."""
    service = EconomicCalendarService(db)
    return await service.get_upcoming(currency=currency, limit=limit)


@router.get("/recent", response_model=List[EconomicEventResponse])
async def get_recent_events(
    currency: Optional[str] = Query(None, description="Filter by currency code (e.g. USD, EUR)"),
    limit: int = Query(10, ge=1, le=50, description="Number of events to retrieve"),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve past macroeconomic events (Actual vs Forecast vs Previous results)."""
    service = EconomicCalendarService(db)
    return await service.get_recent(currency=currency, limit=limit)


@router.get("/high-impact", response_model=List[EconomicEventResponse])
async def get_high_impact_events(
    limit: int = Query(10, ge=1, le=50, description="Number of events to retrieve"),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve high impact events."""
    service = EconomicCalendarService(db)
    return await service.get_high_impact(limit=limit)
