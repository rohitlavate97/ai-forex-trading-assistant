from typing import Optional
import redis.asyncio as aioredis
from src.core.config import settings

# Global async redis client
redis_client: Optional[aioredis.Redis] = None


def get_redis_url() -> str:
    """Construct the Redis connection URL."""
    password_part = f":{settings.REDIS_PASSWORD}@" if settings.REDIS_PASSWORD else ""
    return f"redis://{password_part}{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"


async def init_redis() -> aioredis.Redis:
    """Initialize the global Redis connection pool."""
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(
            get_redis_url(),
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
        )
    return redis_client


async def close_redis() -> None:
    """Close the global Redis connection pool."""
    global redis_client
    if redis_client is not None:
        await redis_client.close()
        redis_client = None


async def get_redis() -> aioredis.Redis:
    """Dependency helper to retrieve the Redis client."""
    if redis_client is None:
        await init_redis()
    return redis_client
