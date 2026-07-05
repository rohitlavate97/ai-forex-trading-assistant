# News Intelligence Agent Guide

The **News Intelligence Agent** is responsible for summarizing forex-related news articles, extracting market sentiment, and estimating the impact of news flow on currency pairs. Built with `Pydantic AI`, this agent serves as the qualitative counter-part to the Technical Analysis and Economic Calendar agents.

## Architecture

The News Intelligence Module consists of:
1.  **NewsArticle Model & DB Layer**: Stores headlines, URLs, published timestamps, source, summary, and sentiment data (`bullish`, `bearish`, `neutral`).
2.  **NewsIntelligenceService**: Orchestrates logic for querying recent, bullish, and bearish news across currency pairs.
3.  **FastAPI Router (`/api/v1/news`)**: Provides RESTful endpoints for the frontend to quickly fetch sentiment data without invoking the LLM.
4.  **News Intelligence Agent**: A specialized `Pydantic AI` agent with prompt-engineered instructions and integrated tool calls.

### Schema (NewsArticle)
- `title` (String): Headline of the news article.
- `url` (String, Optional): Link to the full article.
- `source` (String): Origin publisher (e.g., Reuters, Bloomberg).
- `summary` (String): Brief summary.
- `published_at` (DateTime, UTC).
- `sentiment` (Enum): `bullish`, `bearish`, `neutral`.
- `sentiment_score` (Float): Ranging from -1.0 to +1.0.
- `currency_tags` (String): Comma-separated affected currencies (e.g., "USD,EUR").

## Agent Implementation

The agent uses a strict system prompt that mandates:
- **Probabilistic Language**: It must avoid guarantees (e.g., "price will go up") and instead use "historically correlates with" or "suggests increased probability of".
- **Data Grounding**: It must cite precise scores and headlines returned by the tools.
- **AI Disclaimer**: All analyses must include a mandatory disclaimer.

### Available Tools
- `get_recent_news(currency, sentiment, limit)`: Returns the most recent news matching the tags.
- `get_bullish_news(limit)`: Returns top news sorted by highest positive sentiment score.
- `get_bearish_news(limit)`: Returns top news sorted by strongest negative sentiment score.

## Endpoints

- `GET /api/v1/news/recent`: Fetch recent news (optional `currency`, `sentiment` filters).
- `GET /api/v1/news/bullish`: Fetch top bullish news.
- `GET /api/v1/news/bearish`: Fetch top bearish news.

## Testing
The `pytest` suite covers:
- Correct execution of queries mapping to `bullish`, `bearish`, and `recent` filters.
- Agent compilation and tool bindings using Dependency Injection (`RunContext[AsyncSession]`).
