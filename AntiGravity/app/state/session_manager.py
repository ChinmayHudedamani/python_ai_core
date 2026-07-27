# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Redis Hashes Session State Manager (Strict Zero In-Memory Dicts)

import json
from typing import Dict, Any, Optional
from redis.asyncio import Redis

DEFAULT_SESSION_TTL_SECONDS = 2700  # 45 Minutes


class RedisSessionStateManager:
    """Production Redis Async Session State Manager using Atomic Redis Hashes (HSET / HGETALL)."""

    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    def _format_key(self, phone_number: str) -> str:
        clean_phone = phone_number.replace("+", "").replace("-", "").strip()
        return f"apex:session:{clean_phone}"

    async def get_session(self, phone_number: str) -> Dict[str, str]:
        """Atomic HGETALL fetching all key-value pairs from session hash."""
        key = self._format_key(phone_number)
        raw_hash = await self.redis.hgetall(key)
        return {k.decode("utf-8"): v.decode("utf-8") for k, v in raw_hash.items()} if raw_hash else {}

    async def get_field(self, phone_number: str, field: str) -> Optional[str]:
        """Atomic HGET for a single session field."""
        key = self._format_key(phone_number)
        val = await self.redis.hget(key, field)
        return val.decode("utf-8") if val else None

    async def set_session_field(self, phone_number: str, field: str, value: Any, ttl_seconds: int = DEFAULT_SESSION_TTL_SECONDS) -> bool:
        """Atomic HSET for a single field, avoiding race conditions on rapid double-texts."""
        key = self._format_key(phone_number)
        str_val = json.dumps(value) if isinstance(value, (dict, list, bool)) else str(value)
        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.hset(key, field, str_val)
            pipe.expire(key, ttl_seconds)
            await pipe.execute()
        return True

    async def set_session_bulk(self, phone_number: str, mapping: Dict[str, Any], ttl_seconds: int = DEFAULT_SESSION_TTL_SECONDS) -> bool:
        """Atomic multi-field HSET update."""
        key = self._format_key(phone_number)
        serialized_mapping = {
            k: (json.dumps(v) if isinstance(v, (dict, list, bool)) else str(v))
            for k, v in mapping.items()
        }
        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.hset(key, mapping=serialized_mapping)
            pipe.expire(key, ttl_seconds)
            await pipe.execute()
        return True

    async def delete_field(self, phone_number: str, field: str) -> bool:
        """Atomic HDEL for a specific field."""
        key = self._format_key(phone_number)
        await self.redis.hdel(key, field)
        return True

    async def clear_session(self, phone_number: str) -> bool:
        """Deletes session key upon booking completion or explicit reset."""
        key = self._format_key(phone_number)
        await self.redis.delete(key)
        return True

    async def refresh_ttl(self, phone_number: str, ttl_seconds: int = DEFAULT_SESSION_TTL_SECONDS) -> bool:
        """Extends TTL to 45 minutes upon active user interaction."""
        key = self._format_key(phone_number)
        return await self.redis.expire(key, ttl_seconds)
