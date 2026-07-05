# AI Chat Guide

The **AI Chat** module provides a conversational interface for the user to query market conditions, ask for technical/fundamental analysis, and retrieve information from uploaded documents.

## Architecture

This module implements a streaming Server-Sent Events (SSE) endpoint powered by Pydantic AI's streaming response capabilities.

### Agent Definition
The `chat_agent` (found in `src.modules.chat.agent`) is configured with `pydantic-ai` and `OpenAIChatModel`. It uses a strict system prompt prohibiting explicit trade recommendations and guaranteeing probabilistic language.

### Tools
The chat agent is orchestrated to act as a unified interface to the rest of the application. It has access to the following async tools:
1. `search_knowledge_base`: Queries the Qdrant vector database (RAG).
2. `get_live_market_overview`: Fetches live Bid/Ask/Spread from the Redis mock provider.
3. `get_recent_news_sentiment`: Fetches news articles and sentiment scores.
4. `get_recent_macroeconomic_events`: Fetches recent economic events.

The model automatically decides which tools to invoke based on the user's prompt.

### Endpoints
- `POST /api/v1/chat/stream`: Accepts a `ChatRequest` (message string and optional history). Returns an SSE stream yielding JSON objects: `{"text": "chunk"}`. The final event is `data: [DONE]`.

## Frontend Integration
Clients should use the `EventSource` API or fetch-based SSE decoders to consume the `stream` endpoint, dynamically updating the chat UI as tokens arrive.

## Security
This endpoint is protected by the `get_current_user` dependency (JWT Bearer Auth). All database operations via tools are scoped to the authenticated user's session.
