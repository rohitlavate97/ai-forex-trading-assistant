# Fundamental Analysis Agent Guide

The **Fundamental Analysis Agent** combines qualitative news sentiment with quantitative macroeconomic indicators to provide traders with a holistic fundamental view of a currency pair.

## Architecture

This agent acts as a higher-level analytical layer that consumes data from two existing domains:
1. **Economic Calendar**: High-impact macro events (GDP, CPI, Interest Rates).
2. **News Intelligence**: Breaking news articles and NLP sentiment scores.

The agent uses these two data streams to formulate an assessment of fundamental strength or weakness for a currency (or currency pair). Since it relies on existing schemas and databases, there is no new database table created for this specific agent.

## Agent Implementation

The agent is powered by `Pydantic AI` and bound with strict prompt instructions.

### System Prompt Guidelines
1. **Probabilistic Language Only**: Must avoid definitive predictions. It cannot say "USD will rise". It must say "These factors generally support USD strength."
2. **Data Grounding**: The analysis must explicitly reference the macroeconomic figures and sentiment scores returned by the tools.
3. **Mandatory Disclaimer**: Every response concludes with a standard disclaimer reminding the user that the output is probabilistic AI analysis, not financial advice.

### Available Tools
- `get_macroeconomic_data(currency, limit)`: Fetches recent, high-impact economic events from the `EconomicCalendarRepository`.
- `get_news_sentiment_data(currency, limit)`: Fetches recent news headlines and sentiment scores from the `NewsIntelligenceRepository`.

## Testing

The test suite in `test_fundamental_analysis.py` covers:
- Tool execution against mocked repositories (ensuring database sessions aren't inadvertently hit).
- Correct mapping of Pydantic AI context dependencies (`RunContext`).
- Agent initialization and response structures.
