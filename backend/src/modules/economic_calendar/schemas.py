from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from src.modules.economic_calendar.models import EventImportance


class EconomicEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    event_name: str
    country: str
    currency: str
    importance: EventImportance
    event_time: datetime
    actual: Optional[str] = None
    forecast: Optional[str] = None
    previous: Optional[str] = None
