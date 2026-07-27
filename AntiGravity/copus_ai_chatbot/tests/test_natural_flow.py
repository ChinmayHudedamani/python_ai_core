# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Natural Conversational Flow & Side Inquiry Unit Test Suite

import sys
import io
import unittest
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.llm_router import PATIENT_SYSTEM_PROMPT
from app.services.normalizers import augment_short_text


class TestNaturalConversationalFlow(unittest.TestCase):

    def test_01_system_prompt_empathy_rules(self):
        print("\n--- [TEST 1]: System Prompt Empathy & Safety Rules ---")
        self.assertIn("Empathy & Flexibility First", PATIENT_SYSTEM_PROMPT)
        self.assertIn("Strict Clinical Boundaries / Legal Safety", PATIENT_SYSTEM_PROMPT)
        self.assertIn("Zero Robotic Pressure", PATIENT_SYSTEM_PROMPT)
        print("✅ PASSED: System prompt contains all required conversational flow & safety rules.")

    def test_02_side_inquiry_pass_through(self):
        print("\n--- [TEST 2]: Side Inquiry Pass-Through (No Slot Trap) ---")
        session_state = {"last_intent": "SELECTING_SLOT"}
        
        # Test medication query
        res_med = augment_short_text("tablets", session_state)
        self.assertFalse(res_med["was_augmented"])
        self.assertEqual(res_med["augmented_text"], "tablets")
        print("✅ PASSED: Medication inquiry 'tablets' passed through without slot interception.")

        # Test parking query
        res_park = augment_short_text("parking", session_state)
        self.assertFalse(res_park["was_augmented"])
        self.assertEqual(res_park["augmented_text"], "parking")
        print("✅ PASSED: Direction/Parking query 'parking' passed through without slot interception.")


if __name__ == "__main__":
    unittest.main()
