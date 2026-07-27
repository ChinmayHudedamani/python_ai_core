# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Yelahanka Node v0.2 30-Intent Taxonomy Unit Test Suite

import sys
import io
import unittest
import importlib.util
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.schemas import MIDGODentalResponse

# Import TAXONOMY_30_INTENTS dynamically from app.py
app_path = Path(__file__).resolve().parent.parent / "app.py"
spec = importlib.util.spec_from_file_location("app_main", app_path)
app_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_main)


class Test30IntentTaxonomy(unittest.TestCase):

    def test_01_taxonomy_count(self):
        print("\n--- [TEST 1]: 30-Intent Taxonomy Verification ---")
        taxonomy = app_main.TAXONOMY_30_INTENTS
        self.assertEqual(len(taxonomy), 30)
        print(f"✅ PASSED: TAXONOMY_30_INTENTS contains exactly {len(taxonomy)} intents.")

    def test_02_emergency_intent_classification(self):
        print("\n--- [TEST 2]: Emergency Intent Classification ---")
        response = MIDGODentalResponse(
            extracted_name="Ananya Roy",
            extracted_symptom_or_reason="Knocked-out tooth in accident",
            classified_intent="INTENT_TRAUMA_FIRST_AID",
            patient_reply="Please place the knocked-out tooth in cold milk and head to our clinic immediately!"
        )
        self.assertEqual(response.classified_intent, "INTENT_TRAUMA_FIRST_AID")
        print("✅ PASSED: Emergency trauma intent classified correctly.")


if __name__ == "__main__":
    unittest.main()
