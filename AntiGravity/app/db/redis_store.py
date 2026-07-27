# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI / Copus AI — High-Performance Redis Persistence Layer

import json
from typing import Optional, Set, Dict, Any
from app.services.session.models import PatientSession, SaaSPlanTier


class RedisSessionStore:
    """High-performance Redis Persistence Layer for Active Patient Sessions."""

    SESSION_TTL_SECONDS: int = 86400  # 24 Hours

    def __init__(self, redis_client=None) -> None:
        self._redis = redis_client
        self._local_fallback: Dict[str, str] = {}

    def _get_key(self, phone_number: str) -> str:
        return f"apex:session:{phone_number}"

    def save_session(self, session: PatientSession) -> None:
        """Serializes and persists patient session state with 24-hour TTL."""
        key = self._get_key(session.phone_number)
        payload = {
            "session_id": session.session_id,
            "phone_number": session.phone_number,
            "active_tier": session.active_tier.value,
            "hidden_options": list(session.hidden_options),
            "is_authenticated": session.is_authenticated,
            "selected_language": session.selected_language,
            "selected_branch": session.selected_branch,
            "check_in_code": session.check_in_code,
            "is_active": session.is_active,
            "created_at": session.created_at
        }
        json_str = json.dumps(payload)

        if self._redis:
            self._redis.setex(key, self.SESSION_TTL_SECONDS, json_str)
        else:
            self._local_fallback[key] = json_str

    def load_session(self, phone_number: str) -> Optional[PatientSession]:
        """Retrieves and deserializes patient session state from Redis or fallback."""
        key = self._get_key(phone_number)
        if self._redis:
            raw_data = self._redis.get(key)
        else:
            raw_data = self._local_fallback.get(key)

        if not raw_data:
            return None

        if isinstance(raw_data, bytes):
            raw_data = raw_data.decode("utf-8")

        data = json.loads(raw_data)
        return PatientSession(
            session_id=data.get("session_id", "SESS_RESTORED"),
            phone_number=data["phone_number"],
            active_tier=SaaSPlanTier(data["active_tier"]),
            hidden_options=set(data.get("hidden_options", [])),
            is_authenticated=data.get("is_authenticated", False),
            selected_language=data.get("selected_language", "English"),
            selected_branch=data.get("selected_branch", "Yelahanka Node v0.2"),
            check_in_code=data.get("check_in_code"),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at")
        )
