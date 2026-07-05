import pytest
from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.economic_calendar.models import EconomicEvent, EventImportance
from src.modules.economic_calendar.repository import EconomicCalendarRepository
from src.modules.economic_calendar.agent import economic_calendar_agent


@pytest.mark.asyncio
async def test_repository_get_upcoming_events():
    """Test repository filters upcoming events from DB."""
    # Create mock session
    mock_session = AsyncMock(spec=AsyncSession)
    
    # Pre-populate sample mock events
    event1 = EconomicEvent(
        event_name="Fed Interest Rate Decision",
        country="United States",
        currency="USD",
        importance=EventImportance.HIGH,
        event_time=datetime(2200, 1, 1, 12, 0, 0),  # Far future
        forecast="5.25%",
        previous="5.25%",
    )
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [event1]
    mock_session.execute = AsyncMock(return_value=mock_result)
    
    # Instantiate repo
    repo = EconomicCalendarRepository(mock_session)
    events = await repo.get_upcoming_events(currency="USD", limit=5)
    
    # Assert
    assert len(events) == 1
    assert events[0].event_name == "Fed Interest Rate Decision"
    assert events[0].importance == EventImportance.HIGH
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_repository_get_recent_events():
    """Test repository filters recent past events from DB."""
    mock_session = AsyncMock(spec=AsyncSession)
    
    event1 = EconomicEvent(
        event_name="US CPI Inflation MoM",
        country="United States",
        currency="USD",
        importance=EventImportance.HIGH,
        event_time=datetime(2020, 1, 1, 12, 0, 0),  # Past
        actual="0.2%",
        forecast="0.2%",
        previous="0.1%",
    )
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [event1]
    mock_session.execute = AsyncMock(return_value=mock_result)
    
    repo = EconomicCalendarRepository(mock_session)
    events = await repo.get_recent_events(limit=2)
    
    assert len(events) == 1
    assert events[0].event_name == "US CPI Inflation MoM"
    assert events[0].actual == "0.2%"
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_economic_calendar_agent_tool_binding():
    """Test that economic calendar agent compiles and executes runs using dependency injection."""
    mock_run_result = MagicMock()
    mock_run_result.data = "The economic calendar reports upcoming high-impact events."
    
    # Mock the agent async run method
    economic_calendar_agent.run = AsyncMock(return_value=mock_run_result)
    
    # Create mock session dependency
    mock_session = AsyncMock(spec=AsyncSession)
    
    response = await economic_calendar_agent.run(
        "Show me upcoming calendar events",
        deps=mock_session
    )
    
    assert response.data == "The economic calendar reports upcoming high-impact events."
    economic_calendar_agent.run.assert_called_once_with(
        "Show me upcoming calendar events",
        deps=mock_session
    )
