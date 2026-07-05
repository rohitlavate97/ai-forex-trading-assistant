# Milestone 8: News Intelligence Agent

**Status**: Completed
**Tag**: `v0.8-news-intelligence-agent`

## Objective
Develop a qualitative counterpart to the technical analysis tools that can digest breaking news, interpret sentiment, and inform the user of potential impacts on currency valuations.

## Implementation Details
1. **Schema & Database Updates**:
    - Created `NewsArticle` SQLAlchemy model in `backend/src/modules/news_intelligence/models.py`.
    - Generated and verified Alembic migration (`d003_create_news_articles_table.py`) to persist fields like headline, source, sentiment, and currency tags.
2. **Service & Routing**:
    - Built `NewsIntelligenceRepository` to handle SQL statements filtering by sentiment (bullish/bearish) or recent currency news.
    - Implemented `NewsIntelligenceService` and mounted a FastAPI router at `/api/v1/news` to serve frontend clients rapidly.
3. **Pydantic AI Integration**:
    - Migrated agents from `OpenAIModel` to `OpenAIChatModel` + `OpenAIProvider` to support `pydantic-ai` v2.5.0 updates.
    - Created `news_intelligence_agent` mapped with tools to fetch recent, bullish, and bearish news logic.
    - Added rigorous prompt guidelines forcing the agent to use probabilistic language and cite specific market sentiment scores.
4. **Testing & Fixes**:
    - Added tests in `backend/tests/test_news_intelligence.py` for queries and agent behavior.
    - Resolved `pydantic-ai` compatibility bugs, `bcrypt` string length warnings, and mathematical testing edge-cases (RSI zeroes, Fibonacci float precisions).

## Deliverables
- `NewsArticle` model and `d003_create_news_articles_table.py`.
- `news_intelligence_agent` fully tested.
- `docs/news_intelligence_agent_guide.md` documentation.
