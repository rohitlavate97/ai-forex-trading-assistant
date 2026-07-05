from sqlalchemy import Column, String, Float, Text, Enum, ForeignKey, JSON
import sqlalchemy as sa
import enum
from src.core.database import Base

class TradeDirection(str, enum.Enum):
    LONG = "LONG"
    SHORT = "SHORT"

class JournalEntry(Base):
    __tablename__ = "journal_entries"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    currency_pair = Column(String(10), nullable=False)
    direction = Column(Enum(TradeDirection), nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    profit_loss = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True) # Storing list of strings as JSON
    created_at = Column(sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    updated_at = Column(sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)
