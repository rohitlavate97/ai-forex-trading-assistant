# Market Research Agent Guide

The **Market Research Agent** provides traders with a top-level view of currency price action. By analyzing live price ticks and short-term history, it delivers trend summaries, volatility insights, and overall market condition evaluations.

## Architecture

This agent interfaces directly with the `MarketDataService` which queries the Redis cache where live price feeds are ingested. Unlike other agents that query the SQL database for historical persistence, the Market Research Agent focuses on *recent, live* conditions.

## Agent Implementation

Powered by `Pydantic AI`, this agent aggregates statistical observations into qualitative summaries.

### System Prompt Guidelines
1. **Probabilistic Language**: It cannot guarantee trends will continue. It must use phrases like "recent price action suggests..." or "short-term trend indicates...".
2. **Data Grounding**: The agent must explicitly cite prices, spread sizes, variance pips, and trend directions returned by its tools.
3. **No Trade Advice**: The agent describes the market; it does not instruct the user to execute trades.
4. **Mandatory Disclaimer**: Every response concludes with a standard disclaimer reminding the user that the output is probabilistic AI analysis, not financial advice.

### Available Tools
- `get_currency_overview(symbol)`: Returns the current live price and bid/ask spread.
- `get_volatility_summary(symbol, limit)`: Computes the high, low, average, and price variance (in pips) across a recent history window.
- `get_trend_summary(symbol, limit)`: Analyzes the start and end points of a tick window to establish short-term directional bias.

## Testing

The test suite in `test_market_research.py` ensures:
- Robust float comparison when asserting variances.
- Correct integration with the mocked `MarketDataService`.
- Proper handling of edge cases (e.g., missing price history).
