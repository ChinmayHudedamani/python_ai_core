# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# Pytest / Unittest Session Strategy & Dispatcher Map Test Suite

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.session.models import SaaSPlanTier, ActionType, PatientSession
from app.services.session.session_context import SessionContextManager


class TestSessionStrategies(unittest.TestCase):

    def setUp(self):
        self.session_ctx = SessionContextManager()

    def test_tier1_read_once_and_scroll_up_rule(self):
        """Verifies that selecting an informational option permanently hides it."""
        session = PatientSession(session_id="SESS_PYTEST_1", phone_number="+919876543210", active_tier=SaaSPlanTier.TIER_1)
        initial_menu = self.session_ctx.get_available_menu(session)
        self.assertIn("1. Doctor Details", initial_menu)

        # User clicks '1. Doctor Details'
        result = self.session_ctx.execute_option(session, "1. Doctor Details")
        self.assertTrue(result.success)
        self.assertIn("Doctor Details", result.message)

        # Verify option is stripped from subsequent renderings
        updated_menu = self.session_ctx.get_available_menu(session)
        self.assertNotIn("1. Doctor Details", updated_menu)

    def test_disabled_option_reselection_prevention(self):
        """Ensures attempting to re-execute a hidden option returns an unavailable message."""
        session = PatientSession(session_id="SESS_PYTEST_2", phone_number="+919876543210", active_tier=SaaSPlanTier.TIER_1)
        self.session_ctx.execute_option(session, "1. Doctor Details")
        
        # Attempt second execution
        repeat_res = self.session_ctx.execute_option(session, "1. Doctor Details")
        self.assertFalse(repeat_res.success)
        self.assertTrue("not available" in repeat_res.message or "already hidden" in repeat_res.message)

    def test_tier_switching_preserves_session_identity(self):
        """Ensures switching tiers preserves phone number while swapping strategy logic."""
        session = PatientSession(session_id="SESS_PYTEST_3", phone_number="+919876543210", active_tier=SaaSPlanTier.TIER_1)
        self.session_ctx.execute_option(session, "1. Doctor Details")
        
        # Switch to Tier 2
        self.session_ctx.set_tier(session, SaaSPlanTier.TIER_2)
        self.assertEqual(session.active_tier, SaaSPlanTier.TIER_2)
        
        # Verify Tier 2 menu renders and option remains hidden
        tier2_menu = self.session_ctx.get_available_menu(session)
        self.assertIn("4. 📅 Book Appointment (Live Slots)", tier2_menu)
        self.assertNotIn("1. Doctor Details", tier2_menu)


if __name__ == "__main__":
    unittest.main()
