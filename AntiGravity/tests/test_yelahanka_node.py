# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Yelahanka Node v0.2 Unit Test Suite

import sys
import io
import unittest
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.schemas import MIDGODentalResponse
from app.services.llm_client import GeminiMIDGOClient


class TestYelahankaNode(unittest.TestCase):

    def test_01_midgo_schema_validation(self):
        print("\n--- [TEST 1]: Yelahanka Node v0.2 MIDGO Dual-Output Schema ---")
        response = MIDGODentalResponse(
            extracted_name="Rahul Sharma",
            extracted_symptom_or_reason="Severe lower molar toothache",
            classified_intent="BOOKING_SLOT",
            patient_reply="We can certainly assist with your molar pain, Rahul! We have open slots tomorrow at 10:30 AM."
        )
        self.assertEqual(response.extracted_name, "Rahul Sharma")
        self.assertEqual(response.classified_intent, "BOOKING_SLOT")
        print("✅ PASSED: MIDGODentalResponse validated successfully.")

    def test_02_client_wrapper_instantiation(self):
        print("\n--- [TEST 2]: Yelahanka Gemini MIDGO Client Instantiation ---")
        client = GeminiMIDGOClient()
        self.assertEqual(client.model, "gemini-2.5-flash")
        print("✅ PASSED: GeminiMIDGOClient initialized with model 'gemini-2.5-flash'.")


if __name__ == "__main__":
    unittest.main()
