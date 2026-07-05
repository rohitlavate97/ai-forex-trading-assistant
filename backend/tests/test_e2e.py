import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app
from unittest.mock import patch, AsyncMock

@pytest.fixture(autouse=True)
def mock_redis_and_limiter():
    with patch("src.core.redis.aioredis.from_url") as mock_from_url:
        with patch("src.main.ingestion_service.start", new_callable=AsyncMock):
            with patch("src.main.ingestion_service.stop", new_callable=AsyncMock):
                yield

@pytest.fixture
def client():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

@pytest.mark.asyncio
async def test_end_to_end_flow(client: AsyncClient):
    """
    Simulates a high-level API flow to ensure routers are properly connected
    and returning expected basic structures.
    """
    
    # 1. Root Endpoint
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Welcome to the AI Forex Trading Assistant API"
    
    # 2. Journal Endpoint (Unauthenticated Mock)
    response = await client.get("/api/v1/journal/")
    assert response.status_code == 401
    
    # 3. Webhook (Unauthorized due to no token)
    response = await client.post("/api/v1/webhooks/", json={"source": "test", "type": "test", "data": {}})
    assert response.status_code == 401

    # End-to-end integration is considered successful if all routing logic behaves
    # correctly regarding security boundaries without causing internal server errors.
