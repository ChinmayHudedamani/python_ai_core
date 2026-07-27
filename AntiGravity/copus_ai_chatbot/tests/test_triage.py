# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Automated Triage Engine Unit Tests

import sys
import io
import unittest
from pathlib import Path

# Force UTF-8 encoding for Devanagari test cases
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.triage_engine import TriageEngine
from scripts.seed_kb import seed_database


class TestMultilingualTriageEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        seed_database()
        cls.engine = TriageEngine()

    def test_01_english_critical_emergency(self):
        print("\n--- [TEST 1]: English Critical Emergency Triage ---")
        msg = "My son fell down and has a knocked out tooth!"
        result = self.engine.evaluate_message(msg)
        self.assertIsNotNone(result)
        self.assertEqual(result["urgency_level"], "CRITICAL_EMERGENCY")
        print(f"✅ PASSED: '{msg}' -> {result['urgency_level']}")

    def test_02_hinglish_critical_emergency(self):
        print("\n--- [TEST 2]: Hinglish Critical Emergency Triage ---")
        msg = "Mera daant toot gaya aur khoon nikal raha hai"
        result = self.engine.evaluate_message(msg)
        self.assertIsNotNone(result)
        self.assertEqual(result["urgency_level"], "CRITICAL_EMERGENCY")
        print(f"✅ PASSED: '{msg}' -> {result['urgency_level']}")

    def test_03_hindi_devanagari_critical_emergency(self):
        print("\n--- [TEST 3]: Devanagari Hindi Critical Emergency Triage ---")
        msg = "डॉक्टर साहब दांत निकल गया है एक्सीडेंट में"
        result = self.engine.evaluate_message(msg)
        self.assertIsNotNone(result)
        self.assertEqual(result["urgency_level"], "CRITICAL_EMERGENCY")
        print(f"✅ PASSED: '{msg}' -> {result['urgency_level']}")

    def test_04_routine_query_passthrough(self):
        print("\n--- [TEST 4]: Routine Query Pass-through (No Triage Flag) ---")
        msg = "how much for teeth cleaning"
        result = self.engine.evaluate_message(msg)
        self.assertIsNone(result)
        print(f"✅ PASSED: '{msg}' -> Pass-through to standard RAG pipeline (None).")


if __name__ == "__main__":
    unittest.main()
