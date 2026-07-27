# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# Copus AI — Supplemental Modules 1, 2, 3, & 4 Automated Unit Test Suite

import sys
import unittest
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from copus_ai_chatbot.whatsapp_formatter import WhatsAppFormatter
from copus_ai_chatbot.deposit_engine import generate_hold_deposit
from copus_ai_chatbot.care_card_service import send_post_care_card
from copus_ai_chatbot.reception_cache import verify_checkin_code_offline


class TestSupplementalModules(unittest.TestCase):

    def test_01_whatsapp_formatter_constraints(self):
        print("\n--- [TEST 1]: Meta WhatsApp Formatter Constraints ---")
        # Test <= 3 items (Quick Reply Buttons)
        fmt_small = WhatsAppFormatter.format_menu(["Opt 1", "Opt 2"])
        self.assertEqual(fmt_small["type"], "quick_reply_buttons")
        print("✅ PASSED: <= 3 options formatted as quick_reply_buttons.")

        # Test 3 < len <= 10 items (Interactive List Menu)
        fmt_mid = WhatsAppFormatter.format_menu(["Opt 1", "Opt 2", "Opt 3", "Opt 4"])
        self.assertEqual(fmt_mid["type"], "interactive_list_menu")
        print("✅ PASSED: 4 options formatted as interactive_list_menu.")

        # Test > 10 items (Truncated with Next Page)
        fmt_large = WhatsAppFormatter.format_menu([f"Opt {i}" for i in range(1, 15)])
        self.assertEqual(len(fmt_large["options"]), 10)
        self.assertEqual(fmt_large["options"][-1], "10. ➡️ Next Page")
        print("✅ PASSED: > 10 options truncated with '10. ➡️ Next Page'.")

    def test_02_deposit_engine(self):
        print("\n--- [TEST 2]: Micro-Hold Deposit Engine ---")
        res = generate_hold_deposit("APX-9988", amount=200)
        self.assertEqual(res["status"], "PENDING_DEPOSIT")
        self.assertIn("upi://pay?pa=kasthuri@upi&am=200", res["upi_payment_link"])
        self.assertEqual(res["ttl_seconds"], 600)
        print("✅ PASSED: Micro-hold deposit generated with UPI link and 10-min TTL.")

    def test_03_post_care_card(self):
        print("\n--- [TEST 3]: Post-Consultation Digital Care Card ---")
        card = send_post_care_card("+919876543210", procedure_type="EXTRACTION")
        self.assertIn("Tooth Extraction Post-Op Care Card", card)
        self.assertIn("Bite firmly on clean gauze", card)
        self.assertIn("+91-7338350871", card)
        print("✅ PASSED: Digital care card generated with extraction guidelines.")

    def test_04_reception_offline_cache(self):
        print("\n--- [TEST 4]: Offline-First Receptionist Cache ---")
        res = verify_checkin_code_offline("APX-4928")
        self.assertTrue(res["verified"])
        self.assertEqual(res["patient_name"], "Rahul Sharma")
        print("✅ PASSED: Offline check-in code APX-4928 verified successfully.")


if __name__ == "__main__":
    unittest.main()
