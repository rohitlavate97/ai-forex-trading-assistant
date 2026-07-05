from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from src.modules.news_intelligence.models import SentimentType


class NewsArticleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    title: str
    url: Optional[str] = None
    source: str
    summary: str
    published_at: datetime
    sentiment: SentimentType
    sentiment_score: float
    currency_tags: str
