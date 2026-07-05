import uuid
from datetime import datetime, UTC
from enum import Enum
from sqlalchemy import DateTime, String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from src.core.database import Base


class EventImportance(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EconomicEvent(Base):
    __tablename__ = "economic_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(
        String(36),
        default=lambda: str(uuid.uuid4()),
        unique=True,
        index=True,
        nullable=False,
    )
    event_name: Mapped[str] = mapped_column(String(150), nullable=False)
    country: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), index=True, nullable=False)  # USD, EUR, etc.
    importance: Mapped[EventImportance] = mapped_column(
        String(20), default=EventImportance.LOW, index=True, nullable=False
    )
    event_time: Mapped[datetime] = mapped_column(DateTime, index=True, nullable=False)
    
    # Economics details (metrics)
    actual: Mapped[str | None] = mapped_column(String(50), nullable=True)
    forecast: Mapped[str | None] = mapped_column(String(50), nullable=True)
    previous: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Auditing parameters
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(36), nullable=True)

    def __repr__(self) -> str:
        return f"<EconomicEvent name={self.event_name} importance={self.importance}>"
