import uuid
from datetime import datetime, UTC
from enum import Enum
from sqlalchemy import DateTime, String, BigInteger, Float
from sqlalchemy.orm import Mapped, mapped_column
from src.core.database import Base


class SentimentType(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class NewsArticle(Base):
    __tablename__ = "news_articles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(
        String(36),
        default=lambda: str(uuid.uuid4()),
        unique=True,
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False)  # Bloomberg, Reuters, etc.
    summary: Mapped[str] = mapped_column(String(500), nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime, index=True, nullable=False)
    
    # Sentiment analytics
    sentiment: Mapped[SentimentType] = mapped_column(
        String(20), default=SentimentType.NEUTRAL, index=True, nullable=False
    )
    sentiment_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # Range -1.0 to +1.0
    
    # Tagging to filter relevance (comma separated list of tags e.g. "USD,EUR")
    currency_tags: Mapped[str] = mapped_column(String(100), index=True, nullable=False)

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
        return f"<NewsArticle title={self.title[:20]}... sentiment={self.sentiment}>"
