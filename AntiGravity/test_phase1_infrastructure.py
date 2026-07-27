# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Phase 1 Infrastructure & Knowledge Base Unit Tests

import sys
import io
import decimal
import unittest
from pathlib import Path
from decimal import Decimal

# Force UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.models.patient import Patient
from app.models.booking import Booking
from app.models.kb import ClinicProfile, DoctorProfile, ProcedureCatalog, ClinicalTriageRule
from app.sqlite_db import get_sqlite_session, init_sqlite_db
from sqlmodel import select


class TestPhase1Infrastructure(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_sqlite_db()

    def test_01_phonenumbers_validation(self):
        print("\n--- [TEST 1]: Phone Number Validation (Region IN) ---")
        p = Patient()
        
        # Test valid Indian 10-digit number
        valid_phone = p.validate_phone_number("phone_number", "9876543210")
        self.assertEqual(valid_phone, "+919876543210")

        # Test valid formatted +91 number
        valid_phone2 = p.validate_phone_number("phone_number", "+91 98765 43210")
        self.assertEqual(valid_phone2, "+919876543210")

        # Test invalid number raises ValueError
        with self.assertRaises(ValueError):
            p.validate_phone_number("phone_number", "12345")

        print("✅ PASSED: Phone numbers validated and formatted to E164 (+91).")

    def test_02_currency_decimal_integrity(self):
        print("\n--- [TEST 2]: Decimal Currency Integrity ---")
        booking = Booking(amount_paid=Decimal("500.00"))
        self.assertIsInstance(booking.amount_paid, Decimal)
        self.assertEqual(booking.amount_paid, Decimal("500.00"))
        print("✅ PASSED: Booking amount_paid uses strict Decimal type.")

    def test_03_sqlite_kb_queries(self):
        print("\n--- [TEST 3]: SQLite Relational Knowledge Base Queries ---")
        with get_sqlite_session() as session:
            # Query Clinic Profile
            profile = session.exec(select(ClinicProfile)).first()
            self.assertIsNotNone(profile)
            self.assertIn("APEX Dental", profile.name)

            # Query Doctors
            doctors = session.exec(select(DoctorProfile)).all()
            self.assertGreaterEqual(len(doctors), 2)
            self.assertEqual(doctors[0].name, "Dr. Vikram Sharma")

            # Query Procedure Catalog
            procedures = session.exec(select(ProcedureCatalog)).all()
            self.assertGreaterEqual(len(procedures), 4)

            # Query Triage Rules
            triage_rules = session.exec(select(ClinicalTriageRule)).all()
            self.assertGreaterEqual(len(triage_rules), 4)

        print("✅ PASSED: All relational Knowledge Base queries executed successfully.")


if __name__ == "__main__":
    unittest.main()
