import os
from typing import Any, Dict, List, Optional
import httpx
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_PREFIX = "/api/v1"


class ForexAPIClient:
    """Client wrapper to consume FastAPI endpoints from the Gradio UI."""

    def __init__(self, base_url: str = BACKEND_URL) -> None:
        self.base_url = base_url.rstrip("/")

    def _get_url(self, endpoint: str) -> str:
        return f"{self.base_url}{API_PREFIX}/{endpoint.lstrip('/')}"

    async def get_live_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch current cached tick rate data for a currency pair."""
        url = self._get_url(f"market-data/price/{symbol}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=2.0)
                if response.status_code == 200:
                    return response.json()
        except httpx.HTTPError:
            pass
        return None

    async def get_price_history(self, symbol: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch recent cached ticks history for a currency pair."""
        url = self._get_url(f"market-data/history/{symbol}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params={"limit": limit}, timeout=2.0)
                if response.status_code == 200:
                    return response.json()
        except httpx.HTTPError:
            pass
        return []

    async def get_feed_metrics(self, symbol: str) -> Dict[str, Any]:
        """Fetch tick feed error and telemetry metrics for a pair."""
        url = self._get_url(f"market-data/metrics/{symbol}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=2.0)
                if response.status_code == 200:
                    return response.json()
        except httpx.HTTPError:
            pass
        return {"symbol": symbol, "rejected_ticks_count": 0}
