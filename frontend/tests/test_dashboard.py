import pytest
from unittest.mock import AsyncMock, MagicMock
import httpx
from src.api_client import ForexAPIClient


@pytest.mark.asyncio
async def test_get_live_price_success():
    """Test that ForexAPIClient returns a dictionary on successful 200 GET."""
    client = ForexAPIClient(base_url="http://mock-backend")
    
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"symbol": "EUR/USD", "price": 1.0850}
    
    # Mock AsyncClient.get method
    with pytest.MonkeyPatch.context() as mp:
        mock_get = AsyncMock(return_value=mock_response)
        mp.setattr("httpx.AsyncClient.get", mock_get)
        
        result = await client.get_live_price("EUR/USD")
        
        assert result is not None
        assert result["symbol"] == "EUR/USD"
        assert result["price"] == 1.0850
        # Check target endpoint URL
        mock_get.assert_called_once_with(
            "http://mock-backend/api/v1/market-data/price/EUR/USD",
            timeout=2.0
        )


@pytest.mark.asyncio
async def test_get_live_price_failure():
    """Test that ForexAPIClient returns None when backend returns an error code or throws HTTPError."""
    client = ForexAPIClient(base_url="http://mock-backend")
    
    # Mock GET to raise HTTPError
    with pytest.MonkeyPatch.context() as mp:
        mock_get = AsyncMock(side_effect=httpx.HTTPError("Connection failed"))
        mp.setattr("httpx.AsyncClient.get", mock_get)
        
        result = await client.get_live_price("EUR/USD")
        
        assert result is None


@pytest.mark.asyncio
async def test_get_price_history_success():
    """Test retrieving historical ticks array successfully."""
    client = ForexAPIClient(base_url="http://mock-backend")
    
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"symbol": "EUR/USD", "price": 1.0850},
        {"symbol": "EUR/USD", "price": 1.0848}
    ]
    
    with pytest.MonkeyPatch.context() as mp:
        mock_get = AsyncMock(return_value=mock_response)
        mp.setattr("httpx.AsyncClient.get", mock_get)
        
        result = await client.get_price_history("EUR/USD", limit=2)
        
        assert len(result) == 2
        assert result[0]["price"] == 1.0850
        mock_get.assert_called_once_with(
            "http://mock-backend/api/v1/market-data/history/EUR/USD",
            params={"limit": 2},
            timeout=2.0
        )
