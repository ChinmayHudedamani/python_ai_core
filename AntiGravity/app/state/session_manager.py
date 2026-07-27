# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Redis Hashes & Sliding Window Session Manager (Strict Zero In-Memory Dicts)

import json
from typing import Dict, Any, List, Optional
from redis.asyncio import Redis

DEFAULT_SESSION_TTL_SECONDS = 2700  # 45 Minutes


class RedisSessionStateManager:
    """Production Redis Async Session Manager with LTRIM Sliding Window & State Pinning."""

    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    def _format_key(self, phone_number: str) -> str:
        clean_phone = phone_number.replace("+", "").replace("-", "").strip()
        return f"apex:session:{clean_phone}"

    def _format_window_key(self, phone_number: str) -> str:
        clean_phone = phone_number.replace("+", "").replace("-", "").strip()
        return f"apex:window:{clean_phone}"

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

    # ---------------------------------------------------------
    # 📌 State Pinning Methods
    # ---------------------------------------------------------
    async def pin_state_variables(
        self,
        phone_number: str,
        current_intent: Optional[str] = None,
        identified_doctor: Optional[str] = None,
        held_slot_id: Optional[str] = None,
        ttl_seconds: int = DEFAULT_SESSION_TTL_SECONDS
    ) -> bool:
        """Pins critical context variables into flat Redis Hash fields."""
        mapping = {}
        if current_intent is not None:
            mapping["pinned_current_intent"] = current_intent
        if identified_doctor is not None:
            mapping["pinned_identified_doctor"] = identified_doctor
        if held_slot_id is not None:
            mapping["pinned_held_slot_id"] = held_slot_id

        if not mapping:
            return True

        key = self._format_key(phone_number)
        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.hset(key, mapping=mapping)
            pipe.expire(key, ttl_seconds)
            await pipe.execute()
        return True

    async def get_pinned_state(self, phone_number: str) -> Dict[str, str]:
        """Retrieves pinned state variables for system prompt injection."""
        session = await self.get_session(phone_number)
        return {
            "current_intent": session.get("pinned_current_intent", "GENERAL_INQUIRY"),
            "identified_doctor": session.get("pinned_identified_doctor", "Dr. Chinmay Hudedamani"),
            "held_slot_id": session.get("pinned_held_slot_id", "NONE")
        }

    # ---------------------------------------------------------
    # 🔄 LTRIM Sliding Window Memory Methods (6 Turns Max)
    # ---------------------------------------------------------
    async def add_to_sliding_window(
        self,
        phone_number: str,
        role: str,
        content: str,
        max_turns: int = 6,
        ttl_seconds: int = DEFAULT_SESSION_TTL_SECONDS
    ) -> bool:
        """Adds message turn and uses LTRIM to keep strictly the last 6 messages."""
        key = self._format_window_key(phone_number)
        payload = json.dumps({"role": role, "content": content})

        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.lpush(key, payload)
            pipe.ltrim(key, 0, max_turns - 1)
            pipe.expire(key, ttl_seconds)
            await pipe.execute()
        return True

    async def get_sliding_window(self, phone_number: str, max_turns: int = 6) -> List[Dict[str, str]]:
        """Fetches sliding window turns in chronological order."""
        key = self._format_window_key(phone_number)
        raw_items = await self.redis.lrange(key, 0, max_turns - 1)
        if not raw_items:
            return []

        # LPUSH pushes newest to left; reverse for chronological order
        parsed = [json.loads(item.decode("utf-8")) for item in raw_items]
        parsed.reverse()
        return parsed

    async def clear_session(self, phone_number: str) -> bool:
        """Deletes session hash and sliding window list."""
        key = self._format_key(phone_number)
        window_key = self._format_window_key(phone_number)
        await self.redis.delete(key, window_key)
        return True
