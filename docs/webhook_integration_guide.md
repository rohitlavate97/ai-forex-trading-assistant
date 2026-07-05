# Webhook Integration Guide

## Overview
The External Webhook Integration module provides a standardized way for the AI Forex Trading Assistant to receive and parse real-time signals from third-party platforms.

The primary use case is ingesting alerts from **TradingView**, but the system is designed to be source-agnostic.

## Architecture
- **Router** (`src/modules/webhooks/router.py`): Securely receives `POST` requests and authenticates the sender.
- **Schemas** (`src/modules/webhooks/schemas.py`): Defines the generic wrapper for an alert `WebhookPayload`.
- **Service** (`src/modules/webhooks/service.py`): The command center for acting upon a validated signal (e.g., executing a Celery task or alerting connected WebSockets).

## API Integration

### Endpoint
`POST /api/v1/webhooks/`

### Authentication
All incoming requests **must** provide the header `x-webhook-token`.
The value of this token must strictly match the `SECRET_KEY` configured in the application environment variables.

### Payload Structure
Ensure external services are configured to send JSON matching this schema:

```json
{
  "source": "tradingview",
  "type": "buy_signal",
  "data": {
    "pair": "EURUSD",
    "price": 1.0950,
    "timeframe": "1h",
    "strategy": "MACD_Crossover"
  },
  "timestamp": "2024-06-01T10:00:00Z"
}
```

### Expanding Behavior
To process new sources or types, extend the `WebhookService.process_webhook` method in `service.py`:
```python
if payload.source.lower() == "custom_algo":
    if payload.type == "risk_alert":
        # Dispatch alert to UI
        pass
```
