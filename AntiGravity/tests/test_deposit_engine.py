# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# Pytest / Unittest Micro-Hold Deposit Engine & Persistence Test Suite

import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.deposit_engine import MicroHoldDepositEngine, DepositStatus, HoldDepositRecord
from app.db.redis_store import RedisSessionStore
from app.services.session.models import PatientSession, SaaSPlanTier


class TestDepositEngine(unittest.TestCase):

    def test_deposit_engine_token_entropy_and_utc(self):
        """Verifies 128-bit token entropy (32 hex chars) and UTC expiration key storage."""
        engine = MicroHoldDepositEngine()
        record = engine.create_hold("APX-DEP-01", amount=200)

        token = record.upi_uri.split("Hold-")[1]
        self.assertEqual(len(token), 32)  # 16 bytes = 32 hex chars (128 bits)

        expiry_dt = datetime.fromisoformat(record.expires_at_iso)
        self.assertEqual(expiry_dt.tzinfo, timezone.utc)
        self.assertEqual(record.status, DepositStatus.PENDING)

    def test_redis_session_store_serialization(self):
        """Verifies RedisSessionStore serialization and deserialization of patient session state."""
        store = RedisSessionStore()
        session = PatientSession(
            session_id="SESS_REDIS_1",
            phone_number="+919876543210",
            active_tier=SaaSPlanTier.TIER_3,
            hidden_options={"1. Doctor Details", "💳 3. Cashless TPA Insurance Desk"}
        )

        store.save_session(session)
        loaded = store.load_session("+919876543210")

        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.phone_number, "+919876543210")
        self.assertEqual(loaded.active_tier, SaaSPlanTier.TIER_3)
        self.assertIn("1. Doctor Details", loaded.hidden_options)
        self.assertIn("💳 3. Cashless TPA Insurance Desk", loaded.hidden_options)


if __name__ == "__main__":
    unittest.main()
