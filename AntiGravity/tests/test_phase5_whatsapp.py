"""Phase 5 WhatsApp Webhook Unit Test Suite."""

import sys
import unittest
import asyncio
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.services.whatsapp_client import WhatsAppClient


class TestPhase5WhatsApp(unittest.TestCase):

    def test_01_verify_token_configuration(self):
        print("\n--- [TEST 1]: Meta Webhook Verify Token Configuration ---")
        self.assertEqual(settings.WHATSAPP_VERIFY_TOKEN, "apex_ai_secure_verify_token_2026")
        print("✅ PASSED: Verify Token configured correctly.")

    def test_02_outbound_whatsapp_simulation(self):
        print("\n--- [TEST 2]: Outbound WhatsApp Simulation ---")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        client = WhatsAppClient()
        res = loop.run_until_complete(client.send_text_message("+919876543210", "Test message"))
        loop.close()

        self.assertEqual(res["messaging_product"], "whatsapp")
        print("✅ PASSED: Outbound WhatsApp simulation dispatched successfully.")


if __name__ == "__main__":
    unittest.main()
