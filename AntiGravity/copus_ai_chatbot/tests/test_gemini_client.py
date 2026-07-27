"""Gemini Client Wrapper Unit Test Suite."""

import sys
import unittest
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.services.llm_client import GeminiClientWrapper


class TestGeminiClient(unittest.TestCase):

    def test_01_client_initialization(self):
        print("\n--- [TEST 1]: Gemini Client Initialization & Key Detection ---")
        wrapper = GeminiClientWrapper()
        self.assertEqual(wrapper.model, "gemini-2.5-flash")
        self.assertIsNotNone(wrapper.client)
        print(f"✅ PASSED: GeminiClientWrapper initialized with model '{wrapper.model}'.")


if __name__ == "__main__":
    unittest.main()
