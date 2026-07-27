# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI / Copus AI — Phase 2 Tier 2 Pro Verification Test Suite

import sys
import unittest
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.session.models import PatientSession, SaaSPlanTier, PriorityLevel
from app.services.session.tier2_strategy import Tier2Strategy
from app.services.session.session_context import SessionContextManager
from app.services.whatsapp_formatter import WhatsAppFormatter, FormattedMenuPayload
from app.services.deposit_engine import MicroHoldDepositEngine, HoldDepositRecord


class TestPhase2Tier2Pro(unittest.TestCase):

    def setUp(self):
        self.context_mgr = SessionContextManager()
        self.session = PatientSession(
            session_id="SESS_P2_TEST",
            phone_number="+919876543210",
            active_tier=SaaSPlanTier.TIER_2
        )
        self.tier2_strat = Tier2Strategy()

    def test_01_dispatcher_map_constant_time_lookup(self):
        print("\n--- [TEST 1]: Tier 2 Dispatcher Map Constant Time Lookup ---")
        self.assertIn("1. Doctor Details", self.tier2_strat._dispatcher_map)
        self.assertIn("4. 📅 Book Appointment (Live Slots)", self.tier2_strat._dispatcher_map)
        print("✅ PASSED: Dispatcher map contains all 8 Tier 2 handler mappings.")

    def test_02_option_hiding_rule(self):
        print("\n--- [TEST 2]: Read Once & Scroll Up Option Hiding ---")
        menu_before = self.context_mgr.get_available_menu(self.session)
        self.assertIn("1. Doctor Details", menu_before)

        res = self.context_mgr.execute_option(self.session, "1. Doctor Details")
        self.assertTrue(res.success)

        menu_after = self.context_mgr.get_available_menu(self.session)
        self.assertNotIn("1. Doctor Details", menu_after)
        print("✅ PASSED: '1. Doctor Details' hidden permanently for session.")

    def test_03_surgical_priority_conflict_engine(self):
        print("\n--- [TEST 3]: Surgical Priority Conflict Engine & Check-In Code ---")
        res = self.tier2_strat.resolve_slot_conflict(
            appointment_id="APX-7712",
            requesting_priority=PriorityLevel.SURGICAL_PRIORITY,
            session=self.session
        )
        self.assertTrue(res.success)
        self.assertEqual(res.payload["check_in_code"], "APX-7712")
        self.assertEqual(res.payload["priority"], "SURGICAL_PRIORITY")
        self.assertIn("SURGICAL PRIORITY SLOT LOCKED", res.message)
        print(f"✅ PASSED: Surgical Priority slot locked with Check-In Code {res.payload['check_in_code']}.")

    def test_04_micro_hold_deposit_engine(self):
        print("\n--- [TEST 4]: Micro-Hold Deposit Engine & UPI Expiry ---")
        engine = MicroHoldDepositEngine()
        record: HoldDepositRecord = engine.create_hold("APX-8821", amount=200)
        self.assertEqual(record.status, "PENDING")
        self.assertIn("upi://pay?pa=kasthuri@upi&am=200", record.upi_payment_link)
        self.assertFalse(record.is_expired())
        self.assertEqual(record.ttl_seconds, 600)
        print("✅ PASSED: Micro-hold deposit created with 10-minute UTC TTL.")

    def test_05_whatsapp_formatter_payloads(self):
        print("\n--- [TEST 5]: Meta WhatsApp Formatter Menu Payloads ---")
        menu = self.context_mgr.get_available_menu(self.session)
        payload: FormattedMenuPayload = WhatsAppFormatter.format_menu(menu)
        self.assertEqual(payload.payload_type, "INTERACTIVE_LIST_MENU")
        self.assertEqual(len(payload.options), len(menu))
        print("✅ PASSED: Menu options formatted into FormattedMenuPayload successfully.")


if __name__ == "__main__":
    unittest.main()
