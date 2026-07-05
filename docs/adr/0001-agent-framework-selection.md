# Architectural Decision Record (ADR) - 0001: AI Agent Framework Selection

*   **Status**: Accepted
*   **Decided By**: Antigravity (AI Architect) & Rohit (Lead Engineer)
*   **Date**: 2026-07-05

---

## Context and Problem Statement

The AI Forex Trading Assistant requires a sophisticated multi-agent system. We need:
1.  **Specialist Agents**: Narrow-scoped agents focusing on specific financial tasks (Technical Analysis, News & Sentiment, Risk Management, etc.).
2.  **Coordinator Agent**: A central agent orchestrating conversations, maintaining shared state memory, routing user intents to the correct specialist, and merging analysis results.
3.  **Strict Type Safety & Validations**: Financial data (prices, pip spreads, account balances, position sizing calculations) must be strictly validated before processing or outputting.
4.  **Extensibility**: The ability to migrate agents into separate microservices later without rewriting core logic.

We must choose the framework(s) to build and coordinate these agents.

---

## Considered Alternatives

1.  **Option A: LangChain / LangGraph (Full Stack)**
    *   *Description*: Use LangChain for the individual agents and LangGraph for the multi-agent graph orchestration.
2.  **Option B: CrewAI or AutoGen**
    *   *Description*: Use high-level multi-agent orchestration frameworks.
3.  **Option C: Pydantic AI (Specialists) + LangGraph (Coordinator)**
    *   *Description*: Build individual agent logic and tools using Pydantic AI. Use LangGraph as the orchestrator node graph to handle states, memory, and routing.

---

## Decision Outcome

**Chosen Option**: **Option C: Pydantic AI (Specialist Agents) + LangGraph (Coordinator)**

### Justification

*   **Type Safety (Pydantic v2)**: Pydantic AI is built natively on Pydantic v2. This gives us compiler-level type verification, automatic DTO schemas generation, and robust data checks for financial variables, directly resolving risk analysis requirements.
*   **Structured Output & Tool Binding**: Pydantic AI has the cleanest interface for defining structured outputs and binding tools (which are simply type-hinted python functions).
*   **Cyclic Graphs (LangGraph)**: Multi-agent interaction, feedback loops (e.g. Risk Agent rejecting a proposed trade from the Journal Agent, needing modifications), and long-running state tracking require cyclic graphs. LangGraph is state-of-the-art for cyclic state machine orchestration.
*   **Isolation**: By writing specialists in Pydantic AI, each agent is a self-contained Python module with clear input schemas and output schemas. They can be tested independently or wrapped into microservices.

---

## Pros and Cons of Option C

### Pros
*   **Developer Experience**: High developer speed due to autocompletions and IDE type validation.
*   **Robustness**: Drastically reduced LLM hallucination rate regarding tool-calling parameters, as Pydantic AI handles Pydantic schema generation and enforcement out of the box.
*   **Flexibility**: The Coordinator (LangGraph) can orchestrate any specialist nodes, regardless of whether a particular node is powered by Pydantic AI, a simple heuristic function, or a different LLM tool.

### Cons
*   **Learning Curve**: Requires understanding two frameworks (`pydantic-ai` and `langgraph`) instead of one monolithic library.
*   **Maturity**: `pydantic-ai` is newer than LangChain, which may require us to build custom adapters for some complex retrieval features. (Mitigated by combining it with `llama-index` for vector DB RAG).
