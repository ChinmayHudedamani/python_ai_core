# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Redis Hashes, Sliding Window & Structured Slot Cache Session Manager

import re
import json
from typing import Dict, Any, List, Optional
from redis.asyncio import Redis

DEFAULT_SESSION_TTL_SECONDS = 2700  # 45 Minutes


class RedisSessionStateManager:
    """Production Redis Async Session Manager with LTRIM Sliding Window & Ambiguity-Free Slot Cache."""

    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    def _format_key(self, phone_number: str) -> str:
        clean_phone = phone_number.replace("+", "").replace("-", "").strip()
        return f"apex:session:{clean_phone}"

    def _format_window_key(self, phone_number: str) -> str:
        clean_phone = phone_number.replace("+", "").replace("-", "").strip()
        return f"apex:window:{clean_phone}"

    def _format_slot_cache_key(self, phone_number: str) -> str:
        clean_phone = phone_number.replace("+", "").replace("-", "").strip()
        return f"apex:slots:{clean_phone}"

    async def get_session(self, phone_number: str) -> Dict[str, str]:
        """Atomic HGETALL fetching all key-value pairs from session hash."""
        key = self._format_key(phone_number)
        raw_hash = await self.redis.hgetall(key)
        return {k.decode("utf-8"): v.decode("utf-8") for k, v in raw_hash.items()} if raw_hash else {}

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
    # 🎯 Ambiguity-Free Structured Slot Cache
    # ---------------------------------------------------------
    async def cache_active_slots(
        self,
        phone_number: str,
        slots_list: List[Dict[str, Any]],
        ttl_seconds: int = DEFAULT_SESSION_TTL_SECONDS
    ) -> bool:
        """Saves available slot inventory into Redis with normalized index and time key mappings."""
        if not slots_list:
            return False

        key = self._format_slot_cache_key(phone_number)
        cache_map = {}

        ordinal_words = ["first", "second", "third", "fourth", "fifth"]

        for idx, slot in enumerate(slots_list, start=1):
            slot_json = json.dumps(slot)
            # Index mappings: "1", "2", "3"
            cache_map[str(idx)] = slot_json
            if idx <= len(ordinal_words):
                cache_map[ordinal_words[idx - 1]] = slot_json

            # Time string mappings: "10:30 AM", "10:30", "1030"
            raw_time = slot.get("time", "").lower().strip()
            if raw_time:
                cache_map[raw_time] = slot_json
                clean_time = re.sub(r"[^\d:]", "", raw_time)
                if clean_time:
                    cache_map[clean_time] = slot_json

        serialized_payload = json.dumps(cache_map)
        await self.redis.setex(key, ttl_seconds, serialized_payload)
        return True

    async def get_active_slots_cache(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """Fetches active slot cache dictionary from Redis."""
        key = self._format_slot_cache_key(phone_number)
        raw_val = await self.redis.get(key)
        if raw_val:
            return json.loads(raw_val)
        return None

    async def match_cached_slot(self, phone_number: str, user_message: str) -> Optional[Dict[str, Any]]:
        """Deterministic Interceptor: Matches user message against cached slot keys."""
        cache = await self.get_active_slots_cache(phone_number)
        if not cache:
            return None

        clean_msg = user_message.lower().strip()

        # Check direct key match (e.g. "1", "2", "first", "10:30 am")
        if clean_msg in cache:
            return json.loads(cache[clean_msg])

        # Check regex numeric match (e.g. "slot 1", "option 2", "#1")
        num_match = re.search(r"\b([1-9])\b", clean_msg)
        if num_match and num_match.group(1) in cache:
            return json.loads(cache[num_match.group(1)])

        return None

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

        parsed = [json.loads(item.decode("utf-8")) for item in raw_items]
        parsed.reverse()
        return parsed

    async def clear_session(self, phone_number: str) -> bool:
        """Deletes session hash, sliding window, and slot cache."""
        key = self._format_key(phone_number)
        window_key = self._format_window_key(phone_number)
        cache_key = self._format_slot_cache_key(phone_number)
        await self.redis.delete(key, window_key, cache_key)
        return True
