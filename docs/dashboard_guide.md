# Feature Guide - Gradio Dashboard Layout & Polling

This guide documents the design aesthetics, layouts, timer polling, custom CSS styles, and client-side data querying for the Forex Dashboard.

---

## 1. Business Requirement

*   **Near-Real-Time Visualization**: Display live bid/ask quotes, daily high/low limits, spreads, and percentage changes for tracked forex pairs.
*   **Watchlist Management**: Let users pin specific pairs dynamically to customize their workspace.
*   **Market Summary**: Render top movers by price changes to highlight active trading opportunities.
*   **Aesthetics**: Provide a professional fintech UI (dark mode with clear colors, monospace digits, visual trend indicators) matching production finance standards.

---

## 2. Financial & Domain Context

The Dashboard represents active market states:
*   **Active Bid/Ask Quotes**: Bid and Ask prices are dynamically rendered in monospace font to ensure character widths don't jitter during tick updates.
*   **Real-time Spread Tracker**: Computes active spread in pips (`(Ask - Bid) / pip_size`) to indicate transaction costs before traders open mock positions.
*   **Movers Ranking**: Lists tracked currency pairs sorted descending by absolute change percentage, highlighting volatility.

---

## 3. Frontend Architecture

Gradio does not naturally support persistent push-based WebSocket channels back to browsers due to its architecture. To implement near-real-time updates safely, we split tasks:

```
                  FastAPI Server
                        │
                        ▼ (write tick)
                   Redis Cache
                        │
                        ▼ (poll REST API)
[ForexAPIClient] (frontend/src/api_client.py)
                        │
                        ▼ (yield updates)
      [Gradio UI] (frontend/app.py - Timer Loop)
```

1.  **Backend Ingestion**: FastAPI maintains WebSocket feeds from providers and streams prices continuously to Redis.
2.  **REST API**: FastAPI exposes `/api/v1/market-data/price/{symbol}` to read Redis values in O(1) time.
3.  **Timer Polling**: Gradio utilizes `gr.Timer(2.0)` to periodically trigger an async HTTP client call (`ForexAPIClient`) to fetch active quotes, rebuild HTML templates, and swap component values, avoiding browser freezes.

---

## 4. Gradio Theme & Style Customization

The dashboard styling is governed by [frontend/src/theme.css](file:///D:/Projects/Full%20Stack%20apps/ai-forex-trading-assistant/frontend/src/theme.css):
*   **Theme colors**: Defined via CSS variables (`--bg-primary`, `--bg-card`, `--color-up`, `--color-down`).
*   **Custom Cards**: The class `.forex-card` applies glassmorphism effects, borders, paddings, and translate animations on mouse hover.
*   **Up/Down Badges**: Class `.price-up` and `.price-down` map green and red highlights to quote changes.

---

## 5. API Client Design

The frontend queries the API via `ForexAPIClient` in [frontend/src/api_client.py](file:///D:/Projects/Full%20Stack%20apps/ai-forex-trading-assistant/frontend/src/api_client.py):
*   `get_live_price(symbol)`: Queries active quotes. Returns `None` on HTTP errors, keeping the UI running.
*   `get_price_history(symbol, limit)`: Fetches recent ticks.
*   `get_feed_metrics(symbol)`: Queries telemetry counts.

---

## 6. Testing

The client-side request layer is covered by tests in [frontend/tests/test_dashboard.py](file:///D:/Projects/Full%20Stack%20apps/ai-forex-trading-assistant/frontend/tests/test_dashboard.py):
*   `test_get_live_price_success`: Mocks HTTP response 200 to verify payload parses correctly.
*   `test_get_live_price_failure`: Simulates network timeouts (`httpx.HTTPError`) to confirm the client handles errors gracefully without raising crash exceptions.
*   `test_get_price_history_success`: Validates query parameter limits mapping.

---

## 7. Performance & Latency Trade-offs

*   **Polling Interval (2 seconds)**: Balance price freshness against network costs. A 2-second interval is fast enough for decision-support layouts while preventing developer systems from choking on local loop HTTP requests.
*   **Decoupled Card Generation**: Card templates are rendered using custom HTML strings inside `gr.HTML` components. This is significantly faster and more visually premium than nesting complex individual Gradio Textbox and Icon components.

---

## 8. Common Mistakes

*   **Static Globals inside Grids**: Storing prices in global python dictionary variables in Gradio.
    *   *Problem*: If multiple users connect to the Gradio web server, they will overwrite each other's states.
    *   *Solution*: Always query the central database/cache (Redis) via API client on every timer tick to ensure shared, correct states.
*   **Using standard Gradio inputs for dashboards**: Attempting to style standard textboxes to look like price cards.
    *   *Solution*: Use `gr.HTML` components with custom CSS classes for layout control.

---

## 9. Interview Questions

1.  **Why do we use an HTTP polling mechanism for Gradio instead of direct WebSockets push in the browser?**
    *   *Answer*: Gradio acts as a server-side state coordinator. Creating and managing native WebSockets directly in browser client JS requires writing custom HTML/JS interfaces, bypassing Gradio's standard component bindings. Using a `gr.Timer` to poll a highly optimized Redis cache via FastAPI endpoint is extremely robust, simple, clean, and fully consistent with Gradio's state design.
2.  **How do you prevent the UI from freezing or lagging if the backend API slows down during a timer tick?**
    *   *Answer*: The API client methods are async and utilize strict timeouts (e.g. `timeout=2.0`). If a request stalls, the client drops the request and returns `None`, allowing the timer event thread to exit immediately and keep the UI responsive, while rendering the card as briefly offline.
