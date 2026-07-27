# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Phase 3 Payment Integration & Webhook Idempotency Unit Tests

import sys
import io
import hmac
import hashlib
import uuid
import unittest
from decimal import Decimal
from pathlib import Path

# Force UTF-8 encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.payment import RazorpayAdapter


class TestPhase3PaymentIntegration(unittest.TestCase):

    def setUp(self):
        self.adapter = RazorpayAdapter()
        self.secret = "mock_secret_key_12345"

    def test_01_generate_payment_link(self):
        print("\n--- [TEST 1]: Razorpay Payment Link Generation ---")
        booking_id = uuid.uuid4()
        link = self.adapter.generate_payment_link(
            amount=Decimal("500.00"),
            phone="+919876543210",
            booking_id=booking_id
        )
        self.assertTrue(link.startswith("https://rzp.io/i/"))
        print(f"✅ PASSED: Generated payment link -> {link}")

    def test_02_hmac_sha256_signature_verification(self):
        print("\n--- [TEST 2]: HMAC SHA256 Signature Verification ---")
        payload = b'{"event":"payment.captured","payment_id":"pay_123456"}'
        valid_sig = hmac.new(self.secret.encode(), payload, hashlib.sha256).hexdigest()

        # Valid signature
        self.assertTrue(self.adapter.verify_signature(payload, valid_sig, self.secret))
        print("✅ PASSED: Cryptographically valid signature verified.")

        # Tampered payload / signature
        invalid_sig = "invalid_signature_hash"
        self.assertFalse(self.adapter.verify_signature(payload, invalid_sig, self.secret))
        print("✅ PASSED: Invalid signature rejected correctly.")


if __name__ == "__main__":
    unittest.main()
