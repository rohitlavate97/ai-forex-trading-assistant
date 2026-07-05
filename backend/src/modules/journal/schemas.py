from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime

class TradeDirection(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"

class JournalEntryBase(BaseModel):
    currency_pair: str = Field(..., example="EUR/USD")
    direction: TradeDirection = Field(..., example="LONG")
    entry_price: float = Field(..., example=1.0950)
    exit_price: Optional[float] = Field(None, example=1.1000)
    profit_loss: Optional[float] = Field(None, example=50.0)
    notes: Optional[str] = Field(None, example="Entered after strong PMI data.")
    tags: Optional[List[str]] = Field(default_factory=list, example=["#NFP", "#trend-following"])

class JournalEntryCreate(JournalEntryBase):
    pass

class JournalEntryUpdate(BaseModel):
    currency_pair: Optional[str] = None
    direction: Optional[TradeDirection] = None
    entry_price: Optional[float] = None
    exit_price: Optional[float] = None
    profit_loss: Optional[float] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None

class JournalEntryResponse(JournalEntryBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
