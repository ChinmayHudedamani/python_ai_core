# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Meta Official WhatsApp Cloud API Unit Test Suite

import sys
import io
import asyncio
import unittest
from pathlib import Path

# Force UTF-8 encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.whatsapp_client import WhatsAppClient
from app.api.whatsapp import WHATSAPP_VERIFY_TOKEN


class TestPhase5WhatsAppIntegration(unittest.TestCase):

    def setUp(self):
        self.client = WhatsAppClient()

    def test_01_verify_token_constant(self):
        print("\n--- [TEST 1]: Meta Webhook Verify Token Configuration ---")
        self.assertEqual(WHATSAPP_VERIFY_TOKEN, "apex_ai_secure_verify_token_2026")
        print(f"✅ PASSED: Verify Token configured correctly -> '{WHATSAPP_VERIFY_TOKEN}'")

    def test_02_outbound_text_message_egress(self):
        print("\n--- [TEST 2]: Outbound WhatsApp Text Message Egress ---")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        res = loop.run_until_complete(
            self.client.send_text_message(
                to_phone="+917338350871",
                message="Your appointment APX-4928 is confirmed for tomorrow at 10:30 AM!"
            )
        )
        loop.close()

        self.assertTrue(res.get("is_mock"))
        self.assertIn("messages", res)
        print("✅ PASSED: Outbound WhatsApp text message dispatched successfully.")

    def test_03_outbound_template_message_egress(self):
        print("\n--- [TEST 3]: Outbound WhatsApp Template Message Egress ---")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        res = loop.run_until_complete(
            self.client.send_template_message(
                to_phone="+917338350871",
                template_name="appointment_reminder_24h",
                components=[]
            )
        )
        loop.close()

        self.assertTrue(res.get("is_mock"))
        self.assertIn("messages", res)
        print("✅ PASSED: 24-Hour WhatsApp template reminder dispatched successfully.")


if __name__ == "__main__":
    unittest.main()
