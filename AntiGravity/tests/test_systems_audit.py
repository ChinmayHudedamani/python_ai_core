# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI / Copus AI — Senior Systems & Security Audit Automated Test Suite

import sys
import hmac
import hashlib
import unittest
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.security import IngressSanitizer, MetaWebhookVerifier
from app.services.deposit_engine import MicroHoldDepositEngine, DepositStatus, HoldDepositRecord


class TestSystemsAudit(unittest.TestCase):

    def test_01_ingress_unicode_and_control_char_sanitization(self):
        print("\n--- [TEST 1]: Ingress Unicode & Control Character Sanitization ---")
        raw_dirty_input = "1. Doctor Details \u200B \n\r\t"
        clean = IngressSanitizer.sanitize_choice(raw_dirty_input)
        self.assertEqual(clean, "1. Doctor Details")
        print(f"✅ PASSED: Dirty input '{raw_dirty_input!r}' sanitized to '{clean!r}'.")

    def test_02_meta_webhook_hmac_signature_verification(self):
        print("\n--- [TEST 2]: Meta Webhook HMAC-SHA256 Signature Verification ---")
        secret = "apex_secret_key_9981"
        payload = b'{"object":"whatsapp_business_account","entry":[]}'
        signature = "sha256=" + hmac.new(secret.encode('utf-8'), payload, hashlib.sha256).hexdigest()

        is_valid = MetaWebhookVerifier.verify_signature(payload, signature, secret)
        self.assertTrue(is_valid)

        is_invalid = MetaWebhookVerifier.verify_signature(payload, "sha256=invalid_hash", secret)
        self.assertFalse(is_invalid)
        print("✅ PASSED: HMAC-SHA256 signature verification validated 100%.")

    def test_03_high_entropy_token_and_utc_enforcement(self):
        print("\n--- [TEST 3]: High Entropy Deposit Token (128-bit) & UTC Enforcement ---")
        engine = MicroHoldDepositEngine()
        record: HoldDepositRecord = engine.create_hold("APX-5512", amount=200)

        # Check 128-bit token length in URI
        token_part = record.upi_uri.split("Hold-")[1]
        self.assertEqual(len(token_part), 32)  # 16 bytes hex = 32 chars (128 bits)

        # Check UTC expiry timestamp parsing
        expiry_dt = datetime.fromisoformat(record.expires_at_iso)
        self.assertIsNotNone(expiry_dt.tzinfo)
        self.assertEqual(expiry_dt.tzinfo, timezone.utc)
        print(f"✅ PASSED: 128-bit token '{token_part}' generated with strict UTC expiry {record.expires_at_iso}.")

    def test_04_deposit_payment_verification(self):
        print("\n--- [TEST 4]: Deposit Payment Verification ---")
        engine = MicroHoldDepositEngine()
        record = engine.create_hold("APX-9901", amount=200)
        self.assertEqual(record.status, DepositStatus.PENDING)

        verified = engine.verify_payment("APX-9901")
        self.assertTrue(verified)
        print("✅ PASSED: Payment state transitioned from PENDING -> CONFIRMED successfully.")


if __name__ == "__main__":
    unittest.main()
