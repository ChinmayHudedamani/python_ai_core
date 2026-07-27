# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Phase 4 RBAC & Doctor Command Center Unit Test Suite

import sys
import io
import unittest
from pathlib import Path

# Force UTF-8 encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.llm_router import is_authorized_doctor, get_agent_context
from app.services.tools import CreateBookingInput


class TestPhase4RBACAndDoctorCommandCenter(unittest.TestCase):

    def test_01_rbac_doctor_authorization(self):
        print("\n--- [TEST 1]: RBAC Phone Number Authorization ---")
        doc_phone = "+917338350871"
        patient_phone = "+919876543210"

        # Verify Doctor Authorization
        self.assertTrue(is_authorized_doctor(doc_phone))
        prompt, registry, role = get_agent_context(doc_phone)
        self.assertEqual(role, "DOCTOR_EXECUTIVE_ASSISTANT")
        self.assertIn("Head Surgeon", prompt)
        print("✅ PASSED: Doctor phone correctly identified -> Loaded Doctor Executive Assistant persona.")

        # Verify Patient Authorization
        self.assertFalse(is_authorized_doctor(patient_phone))
        prompt_p, registry_p, role_p = get_agent_context(patient_phone)
        self.assertEqual(role_p, "PATIENT_CONCIERGE")
        self.assertIn("WhatsApp clinical assistant", prompt_p)
        print("✅ PASSED: Patient phone correctly identified -> Loaded Patient Concierge persona.")

    def test_02_mandatory_symptom_schema(self):
        print("\n--- [TEST 2]: Mandatory Patient Symptom Schema ---")

        # Test valid input with symptoms
        valid_input = CreateBookingInput(
            slot_id="123e4567-e89b-12d3-a456-426614174000",
            patient_id="123e4567-e89b-12d3-a456-426614174001",
            patient_symptoms="Severe molar toothache preventing sleep",
            procedure_name="Microscopic Single-Sitting Root Canal (RCT)"
        )
        self.assertEqual(valid_input.patient_symptoms, "Severe molar toothache preventing sleep")
        print("✅ PASSED: Valid CreateBookingInput schema parsed with mandatory symptoms.")

        # Test missing symptoms raises Pydantic ValidationError
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            CreateBookingInput(
                slot_id="123e4567-e89b-12d3-a456-426614174000",
                patient_id="123e4567-e89b-12d3-a456-426614174001",
                procedure_name="Microscopic Single-Sitting Root Canal (RCT)"
            )
        print("✅ PASSED: Missing patient_symptoms correctly raised ValidationError.")


if __name__ == "__main__":
    unittest.main()
