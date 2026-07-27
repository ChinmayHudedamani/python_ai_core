# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Phase 4.8 Universal Short-Text Context Injection Unit Test Suite

import sys
import io
import unittest
from pathlib import Path

# Force UTF-8 encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.normalizers import augment_short_text


class TestShortTextNormalizer(unittest.TestCase):

    def test_01_affirmative_short_text_augmentation(self):
        print("\n--- [TEST 1]: Affirmative Short-Text Context Augmentation ---")
        state = {"last_intent": "SELECTING_SLOT", "last_topic": "Root Canal"}
        res = augment_short_text("Yes", state)

        self.assertTrue(res["was_augmented"])
        self.assertEqual(res["augmented_text"], "Yes, confirm the pending appointment slot.")
        print(f"✅ PASSED: 'Yes' -> '{res['augmented_text']}'")

    def test_02_pricing_short_text_augmentation(self):
        print("\n--- [TEST 2]: Pricing Short-Text Context Augmentation ---")
        state = {"last_intent": "CHECKING_PRICES", "last_topic": "Implants"}
        res = augment_short_text("Price?", state)

        self.assertTrue(res["was_augmented"])
        self.assertIn("What is the total price", res["augmented_text"])
        print(f"✅ PASSED: 'Price?' -> '{res['augmented_text']}'")

    def test_03_doctor_name_shorthand_augmentation(self):
        print("\n--- [TEST 3]: Doctor Name Shorthand Context Augmentation ---")
        state = {"last_intent": "GENERAL_INQUIRY"}
        res = augment_short_text("Nair", state)

        self.assertTrue(res["was_augmented"])
        self.assertEqual(res["augmented_text"], "Check available appointment slots for Dr. Rajesh Nair.")
        print(f"✅ PASSED: 'Nair' -> '{res['augmented_text']}'")

    def test_04_long_text_pass_through(self):
        print("\n--- [TEST 4]: Long Text Pass-Through (No Augmentation) ---")
        long_msg = "Can I book a consultation with Dr. Sharma for tomorrow at 2 pm?"
        res = augment_short_text(long_msg, {})

        self.assertFalse(res["was_augmented"])
        self.assertEqual(res["augmented_text"], long_msg)
        print("✅ PASSED: Long text passed through without augmentation.")


if __name__ == "__main__":
    unittest.main()
