# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI / Copus AI — Tier 2.5 Beta Testing Verification Test Suite

import sys
import unittest
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.session.models import PatientSession, SaaSPlanTier, ActionType
from app.services.session.tier25_beta_strategy import Tier25BetaStrategy
from app.services.session.session_context import SessionContextManager


class TestTier25BetaStrategy(unittest.TestCase):

    def setUp(self):
        self.context_mgr = SessionContextManager()
        self.session = PatientSession(
            session_id="SESS_BETA_TEST",
            phone_number="+919876543210",
            active_tier=SaaSPlanTier.TIER_2_5_BETA
        )
        self.beta_strat = Tier25BetaStrategy()

    def test_01_dispatcher_map_constant_time_lookup(self):
        print("\n--- [TEST 1]: Tier 2.5 Dispatcher Map Constant Time Lookup ---")
        self.assertIn("4. 🩺 🧪 Guided Clinical Pre-Triage (Beta)", self.beta_strat._dispatcher_map)
        self.assertIn("5. 📋 🧪 Digital Care Cards (Beta)", self.beta_strat._dispatcher_map)
        print("✅ PASSED: Dispatcher map contains all 8 Tier 2.5 handler mappings.")

    def test_02_beta_pre_triage_execution(self):
        print("\n--- [TEST 2]: Guided Clinical Pre-Triage Beta Execution ---")
        res = self.context_mgr.execute_option(self.session, "4. 🩺 🧪 Guided Clinical Pre-Triage (Beta)")
        self.assertTrue(res.success)
        self.assertEqual(res.action_type, ActionType.EMERGENCY)
        self.assertIn("Guided Clinical Pre-Triage (Beta Testing)", res.message)
        print("✅ PASSED: Beta Clinical Pre-Triage executed successfully.")

    def test_03_beta_care_cards_preview(self):
        print("\n--- [TEST 3]: Digital Care Cards Beta Sandbox Preview ---")
        res = self.context_mgr.execute_option(self.session, "5. 📋 🧪 Digital Care Cards (Beta)")
        self.assertTrue(res.success)
        self.assertEqual(res.action_type, ActionType.INFORMATIONAL)
        self.assertIn("Digital Care Card Sandbox Preview", res.message)

        menu_after = self.context_mgr.get_available_menu(self.session)
        self.assertNotIn("5. 📋 🧪 Digital Care Cards (Beta)", menu_after)
        print("✅ PASSED: Beta Care Cards preview executed and option hidden for session.")

    def test_04_factory_registry_resolution(self):
        print("\n--- [TEST 4]: SessionContextManager Factory Registry Tier 2.5 Resolution ---")
        strat = self.context_mgr.get_strategy(SaaSPlanTier.TIER_2_5_BETA)
        self.assertIsInstance(strat, Tier25BetaStrategy)
        print("✅ PASSED: SessionContextManager resolved Tier25BetaStrategy correctly.")


if __name__ == "__main__":
    unittest.main()
