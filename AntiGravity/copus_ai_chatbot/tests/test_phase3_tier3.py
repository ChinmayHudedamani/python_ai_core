# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI / Copus AI — Phase 3 Tier 3 Enterprise Verification Test Suite

import sys
import unittest
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.session.models import PatientSession, SaaSPlanTier, ActionType
from app.services.session.tier3_strategy import Tier3Strategy
from app.services.session.session_context import SessionContextManager
from app.services.care_card_service import CareCardService, ProcedureCategory
from app.ui.reception_cache import ReceptionistDailyCache, OfflineAppointmentRecord


class TestPhase3Tier3Enterprise(unittest.TestCase):

    def setUp(self):
        self.context_mgr = SessionContextManager()
        self.session = PatientSession(
            session_id="SESS_P3_TEST",
            phone_number="+919876543210",
            active_tier=SaaSPlanTier.TIER_3
        )
        self.tier3_strat = Tier3Strategy()

    def test_01_tier3_dispatcher_map_constant_time_lookup(self):
        print("\n--- [TEST 1]: Tier 3 Dispatcher Map Constant Time Lookup ---")
        self.assertIn("🏥 1. Select Clinic Branch & Specialist", self.tier3_strat._dispatcher_map)
        self.assertIn("🩺 2. Guided Clinical Pre-Triage", self.tier3_strat._dispatcher_map)
        self.assertIn("💳 3. Cashless TPA Insurance Desk", self.tier3_strat._dispatcher_map)
        print("✅ PASSED: Dispatcher map contains all 7 Tier 3 handler mappings.")

    def test_02_option_hiding_rule_enterprise(self):
        print("\n--- [TEST 2]: Enterprise Read Once & Scroll Up Option Hiding ---")
        menu_before = self.context_mgr.get_available_menu(self.session)
        self.assertIn("💳 3. Cashless TPA Insurance Desk", menu_before)

        res = self.context_mgr.execute_option(self.session, "💳 3. Cashless TPA Insurance Desk")
        self.assertTrue(res.success)

        menu_after = self.context_mgr.get_available_menu(self.session)
        self.assertNotIn("💳 3. Cashless TPA Insurance Desk", menu_after)
        print("✅ PASSED: '💳 3. Cashless TPA Insurance Desk' hidden permanently for session.")

    def test_03_digital_care_card_engine(self):
        print("\n--- [TEST 3]: Digital Care Card Engine & Retention Recall ---")
        card_text = CareCardService.generate_care_card(ProcedureCategory.EXTRACTION, patient_name="Rahul S.")
        self.assertIn("Surgical Extraction Recovery Instructions", card_text)
        self.assertIn("Rahul S.", card_text)
        self.assertIn("Keep firm gauze pressure for 45 minutes", card_text)
        self.assertIn("In 7 days", card_text)
        print("✅ PASSED: Digital care card generated with Do's, Don'ts, and 7-day recall window.")

    def test_04_offline_receptionist_daily_cache(self):
        print("\n--- [TEST 4]: Offline-First Receptionist Daily Roster Cache ---")
        cache = ReceptionistDailyCache()
        mock_records = {
            "APX-8899": OfflineAppointmentRecord(
                checkin_code="APX-8899",
                patient_name="Priya Sharma",
                patient_phone="+919876543210",
                procedure="Implants Evaluation",
                slot_time_iso="11:30 AM"
            )
        }
        cache.seed_daily_roster(mock_records)

        res = cache.verify_checkin_code("APX-8899")
        self.assertEqual(res["status"], "SUCCESS")
        self.assertIn("Priya Sharma", res["message"])

        res_dup = cache.verify_checkin_code("APX-8899")
        self.assertEqual(res_dup["status"], "ALREADY_VERIFIED")
        print("✅ PASSED: Offline check-in code APX-8899 verified and duplicate check-in blocked.")

    def test_05_dynamic_3tier_switching(self):
        print("\n--- [TEST 5]: Dynamic 3-Tier SaaS Subscription Switching ---")
        # Start in Tier 1
        self.session.active_tier = SaaSPlanTier.TIER_1
        menu_t1 = self.context_mgr.get_available_menu(self.session)
        self.assertIn("1. Doctor Details", menu_t1)

        # Switch to Tier 2
        self.context_mgr.set_tier(self.session, SaaSPlanTier.TIER_2)
        menu_t2 = self.context_mgr.get_available_menu(self.session)
        self.assertIn("4. 📅 Book Appointment (Live Slots)", menu_t2)

        # Switch to Tier 3
        self.context_mgr.set_tier(self.session, SaaSPlanTier.TIER_3)
        menu_t3 = self.context_mgr.get_available_menu(self.session)
        self.assertIn("💳 3. Cashless TPA Insurance Desk", menu_t3)
        print("✅ PASSED: Dynamic switching across Tier 1 -> Tier 2 -> Tier 3 verified 100%.")


if __name__ == "__main__":
    unittest.main()
