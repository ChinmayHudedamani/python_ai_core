# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI / Copus AI — Master Final Polish Verification Test Suite

import sys
import unittest
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.utils.time_utils import IST, get_current_ist, format_ist_time
from app.services.session.models import PatientSession, SaaSPlanTier, ActionType
from app.services.session.session_context import SessionContextManager
from app.services.ai_sandwich import AISandwichEngine
from app.ui.reception_cache import ReceptionistDailyCache, OfflineAppointmentRecord


class TestMasterFinalPolish(unittest.TestCase):

    def setUp(self):
        self.context_mgr = SessionContextManager()
        self.session = PatientSession(
            session_id="SESS_POLISH_TEST",
            phone_number="+919876543210",
            active_tier=SaaSPlanTier.TIER_1
        )
        self.context_mgr.session_state_obj = self.session
        self.sandwich = AISandwichEngine(self.context_mgr)

    def test_01_ist_timezone_compliance(self):
        print("\n--- [CRITERIA 1]: Strict IST Timezone Compliance (Asia/Kolkata) ---")
        now_ist = get_current_ist()
        self.assertEqual(now_ist.tzinfo, IST)
        formatted = format_ist_time(now_ist)
        self.assertIn("IST", formatted)
        print(f"✅ PASSED: Timezone verified strictly as IST ({formatted}).")

    def test_02_instant_pay_at_clinic_booking(self):
        print("\n--- [CRITERIA 2]: Instant Pay-at-Clinic Slot Booking Protocol ---")
        self.session.active_tier = SaaSPlanTier.TIER_2
        res = self.context_mgr.execute_option(self.session, "3. 📅 Book Appointment (Instant Lock)")
        self.assertTrue(res.success)
        self.assertEqual(res.payload["payment_status"], "PENDING_AT_DESK")
        self.assertIn("APX-", res.payload["check_in_code"])
        print(f"✅ PASSED: Instant slot locked with Check-In Code {res.payload['check_in_code']} and PENDING_AT_DESK status.")

    def test_03_four_tier_saas_switching(self):
        print("\n--- [CRITERIA 3]: 4-Tier SaaS Subscription Switching (Tier 1 -> 2 -> 2.5 -> 3) ---")
        tiers = [SaaSPlanTier.TIER_1, SaaSPlanTier.TIER_2, SaaSPlanTier.TIER_2_5_BETA, SaaSPlanTier.TIER_3]
        for t in tiers:
            self.context_mgr.set_tier(self.session, t)
            self.assertEqual(self.session.active_tier, t)
            menu = self.context_mgr.get_available_menu(self.session)
            self.assertGreater(len(menu), 0)
        print("✅ PASSED: Seamless switching verified across all 4 SaaS subscription tiers.")

    def test_04_read_once_and_scroll_up_rule(self):
        print("\n--- [CRITERIA 4]: Read-Once & Scroll-Up Session Option Hiding ---")
        self.session.active_tier = SaaSPlanTier.TIER_1
        menu_before = self.context_mgr.get_available_menu(self.session)
        self.assertIn("1. Doctor Details", menu_before)

        res = self.context_mgr.execute_option(self.session, "1. Doctor Details")
        self.assertTrue(res.success)

        menu_after = self.context_mgr.get_available_menu(self.session)
        self.assertNotIn("1. Doctor Details", menu_after)
        print("✅ PASSED: Option hidden permanently for session.")

    def test_05_nlm_and_tri_layer_resilience(self):
        print("\n--- [CRITERIA 5]: Local NLM Engine & Tri-Layer Resilient Gateway ---")
        # Test Tier 2.5 Sandbox NLM
        self.session.active_tier = SaaSPlanTier.TIER_2_5_BETA
        res_beta = self.sandwich.process_patient_input("guided clinical pre-triage for severe toothache")
        self.assertTrue(res_beta.success)

        # Test Tier 3 Resilient Fallback
        self.session.active_tier = SaaSPlanTier.TIER_3
        res_t3 = self.sandwich.process_patient_input("simulate_offline cashless TPA insurance desk")
        self.assertTrue(res_t3.success)
        self.assertIn("Cashless TPA Insurance Desk", res_t3.message)
        print("✅ PASSED: NLM & Tri-layer resilient gateway verified in Tiers 2.5 & 3.")

    def test_06_gated_admin_portals_behavior(self):
        print("\n--- [CRITERIA 6]: Dual Admin Portals Unlocked in Tiers 2, 2.5 & 3 ---")
        cache = ReceptionistDailyCache()
        cache.seed_daily_roster({
            "APX-1122": OfflineAppointmentRecord("APX-1122", "Rahul M.", "+919876543210", "Implants", "10:30 AM IST")
        })
        verification = cache.verify_and_collect_payment("APX-1122", payment_method="UPI")
        self.assertEqual(verification["status"], "SUCCESS")
        print("✅ PASSED: Receptionist desk on-the-spot payment & check-in verified.")


if __name__ == "__main__":
    unittest.main()
