"""Async Redis connection client initialization."""

from redis.asyncio import Redis, ConnectionPool
from app.core.config import settings

redis_pool = ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=False
)

redis_client = Redis(connection_pool=redis_pool)


async def get_redis_client() -> Redis:
    """Returns async Redis client instance."""
    return redis_client
