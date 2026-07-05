import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.core.config import settings

@pytest.fixture
def client():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

@pytest.mark.asyncio
async def test_webhook_unauthorized(client: AsyncClient):
    payload = {
        "source": "tradingview",
        "type": "buy_signal",
        "data": {"price": 1.0950}
    }
    # No header provided
    response = await client.post("/api/v1/webhooks/", json=payload)
    assert response.status_code == 401
    
    # Wrong header provided
    headers = {"x-webhook-token": "wrong-token"}
    response = await client.post("/api/v1/webhooks/", json=payload, headers=headers)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_webhook_authorized(client: AsyncClient):
    payload = {
        "source": "tradingview",
        "type": "buy_signal",
        "data": {"price": 1.0950}
    }
    
    # Correct header
    headers = {"x-webhook-token": settings.SECRET_KEY}
    response = await client.post("/api/v1/webhooks/", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Webhook processed"
