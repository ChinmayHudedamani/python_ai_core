# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# Pytest Fixtures & In-Memory Redis Mock

import pytest
import sys
from pathlib import Path

# Ensure workspace root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.session.session_context import SessionContextManager
from app.services.session.models import PatientSession, SaaSPlanTier
from app.db.redis_store import RedisSessionStore


class LocalMockRedis:
    """In-memory Redis mock for zero-dependency pytest execution."""
    def __init__(self):
        self._store = {}

    def set(self, key, value):
        self._store[key] = value

    def setex(self, key, time, value):
        self._store[key] = value

    def get(self, key):
        return self._store.get(key)


@pytest.fixture
def mock_redis():
    """Provides an in-memory Redis instance for zero-dependency test runs."""
    return LocalMockRedis()


@pytest.fixture
def redis_store(mock_redis):
    return RedisSessionStore(redis_client=mock_redis)


@pytest.fixture
def session_ctx():
    return SessionContextManager()
