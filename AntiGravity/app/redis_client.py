# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Redis Async Client

import redis.asyncio as redis
from app.config import settings

redis_client = redis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=False
)

async def get_redis_client() -> redis.Redis:
    """Dependency provider for async Redis client."""
    return redis_client
