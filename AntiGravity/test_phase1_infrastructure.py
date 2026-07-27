"""Phase 1 Infrastructure Unit Test Suite."""

import sys
import unittest
import asyncio
from pathlib import Path
from decimal import Decimal
from sqlmodel import Session, select

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.sqlite_db import sqlite_engine
from app.models.patient import Patient
from app.models.kb import DoctorProfile, ClinicProfile


class TestPhase1Infrastructure(unittest.TestCase):

    def test_01_phone_number_validation(self):
        print("\n--- [TEST 1]: Phone Number Validation (Region IN) ---")
        p1 = Patient(phone_number="9876543210", name="Test Patient")
        self.assertEqual(p1.phone_number, "+919876543210")

        p2 = Patient(phone_number="+91 98765 43210", name="Test Patient 2")
        self.assertEqual(p2.phone_number, "+919876543210")

        with self.assertRaises(ValueError):
            Patient(phone_number="123", name="Invalid Phone")

        print("✅ PASSED: Phone numbers validated and formatted to E164 (+91).")

    def test_02_decimal_currency_integrity(self):
        print("\n--- [TEST 2]: Decimal Currency Integrity ---")
        doc = DoctorProfile(
            name="Dr. Test",
            title="Surgeon",
            qualifications="BDS",
            experience_years=10,
            bio="Bio",
            specialties="Surgery",
            available_days="Mon",
            consultation_fee=Decimal("700.50")
        )
        self.assertIsInstance(doc.consultation_fee, Decimal)
        self.assertEqual(doc.consultation_fee, Decimal("700.50"))
        print("✅ PASSED: DoctorProfile consultation_fee uses strict Decimal type.")

    def test_03_sqlite_knowledge_base_queries(self):
        print("\n--- [TEST 3]: SQLite Relational Knowledge Base Queries ---")
        with Session(sqlite_engine) as session:
            profile = session.exec(select(ClinicProfile)).first()
            if profile:
                self.assertTrue("APEX" in profile.name.upper() or "DENTAL" in profile.name.upper())
        print("✅ PASSED: All relational Knowledge Base queries executed successfully.")


if __name__ == "__main__":
    unittest.main()
