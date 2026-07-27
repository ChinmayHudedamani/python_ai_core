# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# Pytest / Unittest Surgical Priority Engine Test Suite

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.session.tier2_strategy import Tier2Strategy
from app.services.session.models import PriorityLevel, PatientSession, SaaSPlanTier


class TestPriorityEngine(unittest.TestCase):

    def test_surgical_priority_overrides_general_consultation(self):
        """Verifies that SURGICAL_PRIORITY takes precedence over GENERAL_CONSULTATION."""
        tier2 = Tier2Strategy()
        session = PatientSession(session_id="SESS_SURG_TEST", phone_number="+919876543210", active_tier=SaaSPlanTier.TIER_2)
        
        conflict_resolution = tier2.resolve_slot_conflict(
            appointment_id="APX-SURG-99",
            requesting_priority=PriorityLevel.SURGICAL_PRIORITY,
            session=session
        )

        self.assertTrue(conflict_resolution.success)
        self.assertEqual(conflict_resolution.payload["check_in_code"], "APX-SURG-99")
        self.assertEqual(conflict_resolution.payload["priority"], "SURGICAL_PRIORITY")
        self.assertIn("SURGICAL PRIORITY SLOT LOCKED", conflict_resolution.message)


if __name__ == "__main__":
    unittest.main()
