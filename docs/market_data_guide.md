# Feature Guide - Market Data Ingestion & Caching

This guide details the real-time forex price ingestion pipeline, validation constraints, connection resiliency strategy, and cache serialization interfaces.

---

## 1. Business Requirement

*   **Real-time Decision Support**: Agents and traders require up-to-date currency quote rates to calculate indicator values, analyze trade patterns, check risk margins, and compute stop-loss levels.
*   **Zero Auto-Execution**: Incoming data is parsed and displayed solely for information and simulated paper trading. No real trades are ever triggered.
*   **High Resilience**: The ingestion system must survive network drops, API disconnects, and malformed quotes without failing or reporting stale prices as active.

---

## 2. Financial & Domain Context

Forex prices are governed by key terminology implemented in our service:
*   **Pip (Percentage in Point)**: The smallest price change a currency pair can make. For `EUR/USD`, 1 pip is `0.0001`. For `USD/JPY`, 1 pip is `0.01`. In our mock generator, price walks apply movements measured in pips.
*   **Bid and Ask**:
    *   **Bid**: The price a buyer is willing to pay (sell price for the trader).
    *   **Ask (Offer)**: The price a seller is willing to accept (buy price for the trader).
    *   **Spread**: The difference between Ask and Bid (`Ask - Bid`). The mock provider simulates spreads to compute realistic transaction costs for paper trading journal reviews.

---

## 3. Ingestion Architecture

```
    WebSocket Market Source (Local Mock / Twelve Data)
                          │
                          ▼ (ws / wss connection)
             [Ingestion Client Service]
                          │
       ┌──────────────────┴──────────────────┐
       ▼ (Invalid/Spike)                     ▼ (Clean Tick)
[Reject & Increment Metric]            [Cache in Redis]
                                             │
                                             ├─► Set "price:SYMBOL" (Active quote)
                                             └─► LPUSH "history:SYMBOL" (History list)
```

1.  **Mock WebSocket Server**: In development mode, runs on `ws://localhost:8765`, broadcasting randomized walks of key forex pairs (`EUR/USD`, `GBP/USD`, `USD/JPY`, `AUD/USD`).
2.  **WebSocket Ingestion Client**: Connects as a background service during FastAPI lifespan boot, continuously reading ticks, validating structures, and writing to Redis.

---

## 4. Relational & Redis Design

We leverage Redis as an in-memory database to store real-time ticks:

### 1. Active Price Cache (`price:<symbol>`)
Stores a JSON representation of the latest validated quote.
*   *Key*: `price:EUR/USD`
*   *Value (JSON)*:
    ```json
    {"symbol": "EUR/USD", "price": 1.0854, "bid": 1.08534, "ask": 1.08546, "timestamp": 1719830400.0, "high": 1.0864, "low": 1.0844}
    ```

### 2. Historical Prices Queue (`history:<symbol>`)
Redis `LIST` structure containing the last **100** ticks.
*   *Key*: `history:EUR/USD`
*   *Operations*: `LPUSH` on new tick, `LTRIM` to index 99.

### 3. Rejection Telemetry Counter (`metrics:rejected_ticks:<symbol>`)
Tracks count of price feed anomalies.
*   *Key*: `metrics:rejected_ticks:EUR/USD`

---

## 5. API Design

Exposed under `/api/v1/market-data`:

| Endpoint | Method | Security | Parameters | Response |
| :--- | :--- | :--- | :--- | :--- |
| `/price/{symbol}` | GET | None | `symbol` (e.g. `EUR/USD`) | Active tick JSON object |
| `/history/{symbol}` | GET | None | `symbol`, `limit` (Query, max 100) | Array of tick JSON objects |
| `/metrics/{symbol}` | GET | None | `symbol` | Counter object (`rejected_ticks_count`) |

---

## 6. Feed Validation & Security

*   **Pydantic Guardrails**:
    *   Price must be strictly positive (`price > 0`).
    *   Timestamp drift protection: Rejects ticks with timestamps in the future (> 5 seconds clock drift) or too far in the past (> 60 seconds stale) to block buffer lag.
*   **Extreme Deviation Checks**:
    *   Compares new prices against the last cached value. If the change exceeds **10%** in a single tick, it is flagged as an anomaly (e.g., flash crash feed glitch) and dropped.
*   **Reconnection Backoff**:
    *   WebSocket connections use exponential backoff with random jitter (`delay = min(base * 2^attempt + random, 60s)`) to prevent slamming api servers during outages.

---

## 7. Frontend Timer Polling

Gradio frontend cannot hold permanent persistent socket channels cleanly. Therefore:
*   FastAPI maintains the persistent WebSockets back to the market providers and streams data to Redis.
*   Gradio components query the REST API `/api/v1/market-data/price/{symbol}` at a defined polling frequency (e.g., every 1–2 seconds) using `gr.Timer` to update quote labels and charts, creating a near-real-time dashboard experience.

---

## 8. Performance

*   **Redis O(1) Speed**: Checking and setting prices in Redis executes in sub-millisecond times, avoiding heavy database disk I/O.
*   **Task Isolation**: Ingestion client runs inside an asynchronous background task, completely decoupled from FastAPI request worker threads.

---

## 9. Common Mistakes

*   **Blocked Event Loops**: Using synchronous libraries (like `time.sleep` or synchronous `urllib`) inside the ingestion service, which blocks the execution of the entire FastAPI application.
    *   *Solution*: Always use `await asyncio.sleep(...)` and async-compatible clients (`websockets`, `aioredis`).
*   **Infinite Retry Loops**: Connecting to a dead API without backoffs, consuming memory and triggering rate limits.
    *   *Solution*: Implement exponential backoff.

---

## 10. Interview Questions

1.  **What is exponential backoff with jitter, and why is it preferred over constant retry loops?**
    *   *Answer*: If a server crashes, constant retries from millions of clients will overload the server the moment it restarts (Thundering Herd problem). Exponential backoff multiplies wait times on each failure, and jitter adds randomness. This spreads out request volumes, allowing the server to boot up safely.
2.  **How do we protect our downstream analysis agents from corrupt market data ticks?**
    *   *Answer*: We validate schemas using Pydantic, drop stale/future timestamps, and execute a price deviation check against the last cached quote. If the price spikes by an unrealistic amount (e.g., >10%), we discard the tick, update a metrics counter, and keep the previous price.
