# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI / Copus AI — IST Native & Pay-at-Clinic Protocol Automated Unit Test Suite

import sys
import unittest
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.utils.time_utils import IST, get_current_ist, format_ist_time
from app.services.session.models import PatientSession, SaaSPlanTier, ActionType
from app.services.session.tier2_strategy import Tier2Strategy
from app.ui.reception_cache import ReceptionistDailyCache, OfflineAppointmentRecord


class TestISTPayAtClinicProtocol(unittest.TestCase):

    def test_01_ist_timezone_formatting(self):
        print("\n--- [TEST 1]: Native IST Timezone Formatting ---")
        now_ist = get_current_ist()
        self.assertEqual(now_ist.tzinfo, IST)
        
        formatted_str = format_ist_time(now_ist)
        self.assertIn("IST", formatted_str)
        print(f"✅ PASSED: Current IST formatted as '{formatted_str}'.")

    def test_02_instant_pay_at_clinic_booking(self):
        print("\n--- [TEST 2]: Instant Pay-at-Clinic Slot Confirmation ---")
        strategy = Tier2Strategy()
        session = PatientSession(session_id="SESS_IST_TEST", phone_number="+919876543210", active_tier=SaaSPlanTier.TIER_2)

        res = strategy.process_option(session, "3. 📅 Book Appointment (Instant Lock)")
        self.assertTrue(res.success)
        self.assertIn("APPOINTMENT CONFIRMED", res.message)
        self.assertIn("Pay at Clinic Desk", res.message)
        self.assertEqual(res.payload["payment_status"], "PENDING_AT_DESK")
        self.assertIsNotNone(session.check_in_code)
        print(f"✅ PASSED: Instant slot confirmed with Check-In Code {session.check_in_code} & status PENDING_AT_DESK.")

    def test_03_reception_desk_payment_collection(self):
        print("\n--- [TEST 3]: Reception Desk On-the-Spot Payment Collection ---")
        cache = ReceptionistDailyCache()
        mock_records = {
            "APX-7711": OfflineAppointmentRecord(
                checkin_code="APX-7711",
                patient_name="Anand Kumar",
                patient_phone="+919876543210",
                procedure="Scaling & Cleaning",
                slot_time_ist="10:30 AM IST",
                amount_due_inr=700
            )
        }
        cache.seed_daily_roster(mock_records)

        # Collect Payment via UPI at Desk
        res = cache.verify_and_collect_payment("APX-7711", payment_method="UPI")
        self.assertEqual(res["status"], "SUCCESS")
        self.assertIn("PAID_AT_DESK (UPI)", mock_records["APX-7711"].payment_status)
        self.assertTrue(mock_records["APX-7711"].is_verified)
        print("✅ PASSED: On-the-spot desk payment collected via UPI and check-in marked SUCCESS!")


if __name__ == "__main__":
    unittest.main()
