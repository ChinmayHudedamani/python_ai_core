# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Code-Based Appointment Confirmation Unit Test Suite

import sys
import io
import uuid
import unittest
from datetime import date, time
from pathlib import Path

# Force UTF-8 encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.models.booking import Booking, BookingStatus
from app.models.slot import Slot, SlotStatus
from app.services.booking_engine import generate_check_in_code


class TestCodeBasedConfirmation(unittest.TestCase):

    def test_01_generate_check_in_code_format(self):
        print("\n--- [TEST 1]: Generate Check-In Code Format ---")
        code = generate_check_in_code()
        self.assertTrue(code.startswith("APX-"))
        self.assertEqual(len(code), 8)
        print(f"✅ PASSED: Generated check-in code format -> '{code}'")

    def test_02_booking_status_enums(self):
        print("\n--- [TEST 2]: Code-Based Booking Enums ---")
        self.assertEqual(BookingStatus.SLOT_HELD.value, "SLOT_HELD")
        self.assertEqual(BookingStatus.CONFIRMED.value, "CONFIRMED")
        self.assertEqual(BookingStatus.CHECKED_IN.value, "CHECKED_IN")
        self.assertEqual(BookingStatus.CANCELLED.value, "CANCELLED")
        print("✅ PASSED: Code-Based BookingStatus enums verified.")


if __name__ == "__main__":
    unittest.main()
