# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Phase 4.6 Dynamic Custom Reason Unit Test Suite

import sys
import io
import unittest
from pathlib import Path
from pydantic import ValidationError

# Force UTF-8 encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.admin_tools import RescheduleCancelInput


class TestDynamicCustomReason(unittest.TestCase):

    def test_01_custom_reason_required_in_schema(self):
        print("\n--- [TEST 1]: Custom Reason Required in RescheduleCancelInput Schema ---")
        
        # Valid input
        valid = RescheduleCancelInput(
            appointment_identifier="APX-4928",
            custom_reason="Emergency surgery in Operation Theatre",
            action_type="RESCHEDULE"
        )
        self.assertEqual(valid.custom_reason, "Emergency surgery in Operation Theatre")
        print(f"✅ PASSED: Valid schema parsed with custom_reason -> '{valid.custom_reason}'")

        # Missing custom_reason raises ValidationError
        with self.assertRaises(ValidationError):
            RescheduleCancelInput(
                appointment_identifier="APX-4928",
                action_type="RESCHEDULE"
            )
        print("✅ PASSED: Missing custom_reason correctly raised ValidationError.")


if __name__ == "__main__":
    unittest.main()
