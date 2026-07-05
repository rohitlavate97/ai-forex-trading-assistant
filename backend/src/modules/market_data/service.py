import json
from typing import List, Optional
from redis.asyncio import Redis
from src.core.redis import get_redis


class MarketDataService:
    """Service layer to query live and historical market price data cached in Redis."""

    def __init__(self, redis_client: Optional[Redis] = None) -> None:
        self.redis_client = redis_client

    async def _get_redis(self) -> Redis:
        if self.redis_client is not None:
            return self.redis_client
        return await get_redis()

    async def get_live_price(self, symbol: str) -> Optional[dict]:
        """Fetch the current price of a currency pair from the Redis cache."""
        redis = await self._get_redis()
        data_str = await redis.get(f"price:{symbol}")
        if not data_str:
            return None
        return json.loads(data_str)

    async def get_price_history(self, symbol: str, limit: int = 50) -> List[dict]:
        """Retrieve recent tick history for a currency pair."""
        redis = await self._get_redis()
        # Cap limit to safe size
        safe_limit = min(max(limit, 1), 100)
        
        # Redis lrange is 0-indexed, inclusive: [0, safe_limit - 1]
        ticks_str = await redis.lrange(f"history:{symbol}", 0, safe_limit - 1)
        if not ticks_str:
            return []
            
        return [json.loads(tick) for tick in ticks_str]

    async def get_metrics(self, symbol: str) -> dict:
        """Retrieve telemetry metrics like tick rejection statistics."""
        redis = await self._get_redis()
        rejections = await redis.get(f"metrics:rejected_ticks:{symbol}")
        return {
            "symbol": symbol,
            "rejected_ticks_count": int(rejections) if rejections else 0
        }
