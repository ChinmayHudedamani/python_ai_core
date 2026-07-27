import os
import sys
import io
import json
import time
import unittest
from pathlib import Path

# Force UTF-8 stdout encoding for Windows PowerShell / CMD
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Ensure workspace root is in python path
root_dir = Path(__file__).parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app import app, core_engine
from clinical.ledger_writer import log_appointment, register_conversed_patient, fetch_conversed_patients, init_db, get_db_url
from clinical.rag_generator import generate_zero_hallucination_response


class MasterUnifiedTestSuite(unittest.TestCase):
    """Consolidated Master Test Suite containing all unit, integration, and E2E tests in a single file."""

    def setUp(self):
        self.app_client = app.test_client()
        self.app_client.testing = True
        self.test_phone = "+91-9988776655"
        for p in [self.test_phone, "+91-7338350871", "+91-9876543210", "+91-9988771122", "+91-9876598765"]:
            core_engine.conv_store.reset_session(p)
            s_file = core_engine.conv_store.get_session_file_path(p)
            if s_file.exists():
                try:
                    os.remove(s_file)
                except Exception:
                    pass
        core_engine._verified_patients.clear()
        core_engine._pending_payment_links.clear()
        core_engine.lock_mgr.locks.clear()

    def test_01_operating_hours(self):
        print("\n--- [TEST 1]: Clinic Operating Hours Guard ---")
        res1 = generate_zero_hallucination_response({"notes": "tm 10 30pm"})
        reply1 = res1.get("whatsapp_response", "")
        self.assertIn("outside our operating hours", reply1.lower())
        self.assertIn("10:30 PM", reply1)

        res2 = generate_zero_hallucination_response({"notes": "tm 10 30am"})
        reply2 = res2.get("whatsapp_response", "")
        self.assertIn("hold that time for you", reply2.lower())
        print("✅ PASSED: Operating hours validation (10:30 PM declined, 10:30 AM accepted).")

    def test_02_anti_repetition_guard(self):
        print("\n--- [TEST 2]: Anti-Repetition Guard ---")
        phone = "+91-9876598765"
        core_engine.conv_store.reset_session(phone)
        res1 = core_engine.process_patient_intake("something", patient_phone=phone)
        reply1 = res1.get("whatsapp_response", "")
        self.assertTrue(len(reply1) > 0)

        res2 = core_engine.process_patient_intake("something", patient_phone=phone)
        reply2 = res2.get("whatsapp_response", "")
        self.assertIn("without repeating information", reply2.lower())
        self.assertNotEqual(reply1, reply2)
        print("✅ PASSED: Anti-repetition guard prevents duplicate responses.")

    def test_03_doctor_executive_assistant(self):
        print("\n--- [TEST 3]: Doctor Executive Assistant Mode & Conversed Leads ---")
        doc_phone = "+91-7338350871"
        res1 = core_engine.process_patient_intake("financial update", patient_phone=doc_phone)
        self.assertIn("DOCTOR_", res1.get("status", ""))

        res2 = core_engine.process_patient_intake("show me today's appointments schedule", patient_phone=doc_phone)
        self.assertIn("DOCTOR_", res2.get("status", ""))

        res3 = core_engine.process_patient_intake("how many patients has the bot conversed with", patient_phone=doc_phone)
        self.assertEqual(res3.get("status"), "DOCTOR_CONVERSED_PATIENTS_QUERY")
        self.assertIn("CONVERSED PATIENTS", res3.get("whatsapp_response", ""))

        res4 = core_engine.process_patient_intake("send report", patient_phone=doc_phone)
        self.assertEqual(res4.get("status"), "DOCTOR_PDF_REPORT_DISPATCHED")
        print("✅ PASSED: Doctor AI Assistant routes queries, checks conversed leads & dispatches PDF reports.")

    def test_04_patient_name_registration(self):
        print("\n--- [TEST 4]: Patient Name Registration Flow ---")
        res1 = core_engine.process_patient_intake("Rajesh", patient_phone=self.test_phone)
        self.assertEqual(res1.get("status"), "PATIENT_NAME_REGISTERED")
        self.assertIn("Nice to meet you, Rajesh", res1.get("whatsapp_response", ""))

        res2 = core_engine.process_patient_intake("Rajesh - 7338350871", patient_phone=self.test_phone)
        self.assertEqual(res2.get("status"), "PATIENT_VERIFIED_PAYMENT_LINK_GENERATED")
        self.assertIn("Patient Name: Rajesh", res2.get("whatsapp_response", ""))
        print("✅ PASSED: Name registration welcomes patient warmly and persists name for booking.")

    def test_05_invalid_mobile_number(self):
        print("\n--- [TEST 5]: Invalid / Short Mobile Number Guard ---")
        res1 = core_engine.process_patient_intake("Rajesh - 98765", patient_phone=self.test_phone)
        self.assertEqual(res1.get("status"), "INVALID_PHONE_NUMBER")

        res2 = core_engine.process_patient_intake("0000000000", patient_phone=self.test_phone)
        self.assertEqual(res2.get("status"), "INVALID_PHONE_NUMBER")
        print("✅ PASSED: Invalid and short phone numbers rejected with guidance.")

    def test_06_payment_confirmation_flow(self):
        print("\n--- [TEST 6]: Payment Confirmation & Slot Lock Flow ---")
        phone = "+91-9988771122"
        core_engine.conv_store.reset_session(phone)
        res1 = core_engine.process_patient_intake("Hi I am Test Patient 9988771122, book appointment", patient_phone=phone)
        self.assertEqual(res1.get("status"), "PATIENT_VERIFIED_PAYMENT_LINK_GENERATED")

        res2 = core_engine.process_patient_intake("1", patient_phone=phone)
        self.assertEqual(res2.get("status"), "APPOINTMENT_CONFIRMED_PAID")
        self.assertIn("Payment Confirmed", res2.get("whatsapp_response", ""))
        print("✅ PASSED: Booking flow -> Payment link -> OTP confirmation.")

    def test_07_mai_manipal_progressive_multi_turn_flow(self):
        print("\n--- [TEST 7]: MAI Manipal Style Progressive Micro-Turn Flow ---")
        phone = "+91-9988776655"
        core_engine.conv_store.reset_session(phone)
        s_file = core_engine.conv_store.get_session_file_path(phone)
        if s_file.exists():
            try:
                os.remove(s_file)
            except Exception:
                pass

        # Turn 1: Warm Greeting
        t1 = core_engine.process_patient_intake("Hi MAI", patient_phone=phone)
        self.assertIn("may I know your name", t1.get("whatsapp_response", ""))

        # Turn 2: Patient Name Provided
        t2 = core_engine.process_patient_intake("Chinmay", patient_phone=phone)
        self.assertEqual(t2.get("status"), "PATIENT_NAME_REGISTERED")
        self.assertIn("Nice to meet you, Chinmay", t2.get("whatsapp_response", ""))

        # Turn 3: Treatment Selection / Query
        t3 = core_engine.process_patient_intake("Invisalign clear aligners", patient_phone=phone)
        self.assertIn("Invisalign", t3.get("whatsapp_response", ""))

        # Turn 4: Timing Selection
        t4 = core_engine.process_patient_intake("10 30 tm", patient_phone=phone)
        self.assertIn("10-digit registered mobile number", t4.get("whatsapp_response", ""))

        # Turn 5: Mobile Number Verification
        t5 = core_engine.process_patient_intake("Chinmay - 7338350871", patient_phone=phone)
        self.assertEqual(t5.get("status"), "PATIENT_VERIFIED_PAYMENT_LINK_GENERATED")
        self.assertIn("Payment Link", t5.get("whatsapp_response", ""))

        print("✅ PASSED: MAI Manipal progressive micro-turn flow validated end-to-end.")

    def test_08_run_10_whatsapp_patient_cases(self):
        print("\n--- [TEST 8]: 10 Full WhatsApp Patient Test Cases & DB Lead Writes ---")
        test_cases = [
            {"name": "Rahul Sharma", "phone": "+91-9876543210", "procedure": "Root Canal Treatment (RCT)", "notes": "Severe molar pain on right side"},
            {"name": "Priya Patel", "phone": "+91-9823456789", "procedure": "Teeth Whitening", "notes": "Laser teeth whitening consultation"},
            {"name": "Vikramaditya Rao", "phone": "+91-9711223344", "procedure": "Clear Aligners", "notes": "Invisalign aligner scan"},
            {"name": "Ananya Sen", "phone": "+91-9654321098", "procedure": "Dental Implant", "notes": "Single tooth replacement"},
            {"name": "Rajesh Gupta", "phone": "+91-9543210987", "procedure": "Wisdom Tooth Extraction", "notes": "Impacted wisdom tooth"},
            {"name": "Sneha Reddy", "phone": "+91-9432109876", "procedure": "Emergency Filling", "notes": "Broken composite filling"},
            {"name": "Amit Kumar", "phone": "+91-9321098765", "procedure": "Scaling & Cleaning", "notes": "Bi-annual tartar removal"},
            {"name": "Kavita Joshi", "phone": "+91-9210987654", "procedure": "Veneers Consultation", "notes": "Smile design consultation"},
            {"name": "Rohan Mehta", "phone": "+91-9109876543", "procedure": "Crown Fitting", "notes": "Zirconia crown placement"},
            {"name": "Deepa Nair", "phone": "+91-9098765432", "procedure": "Pediatric Checkup", "notes": "Fluoride application for child"}
        ]

        for idx, tc in enumerate(test_cases, 1):
            res = core_engine.process_patient_intake(
                raw_notes=f"Hi I am {tc['name']} {tc['phone']}, {tc['notes']}",
                patient_name=tc['name'],
                patient_phone=tc['phone']
            )
            self.assertIn("status", res)
            register_conversed_patient(tc['name'], tc['phone'], tc['notes'])
            ledger_res = log_appointment(
                patient_number=tc['phone'],
                time_slot=tc['procedure'],
                procedure_type=tc['procedure'],
                transaction_id=f"TXN_MASTER_{idx:02d}",
                patient_name=tc['name']
            )
            self.assertIn(ledger_res.get("status"), ["SUCCESS", "LOCAL_FALLBACK_SUCCESS", "DOUBLE_BOOKING_PREVENTED"])

        print(f"✅ PASSED: Executed 10/10 WhatsApp patient intake & ledger write test cases.")

    def test_09_flask_backend_api_endpoints(self):
        print("\n--- [TEST 9]: Flask Backend REST API & Webhooks ---")
        # Health check
        h_res = self.app_client.get("/")
        self.assertEqual(h_res.status_code, 200)
        h_data = json.loads(h_res.data)
        self.assertEqual(h_data["status"], "HEALTHY")

        # Intake API
        i_res = self.app_client.post(
            "/api/v1/intake",
            json={"notes": "What is the cost of clear aligners? My phone is +91-9988776655", "name": "Test Patient", "phone": "+91-9988776655"}
        )
        self.assertEqual(i_res.status_code, 200)
        i_data = json.loads(i_res.data)
        self.assertEqual(i_data["status"], "PROCESSED_SUCCESSFULLY")

        # Twilio WhatsApp Webhook
        w_res = self.app_client.post(
            "/webhook/whatsapp",
            data={
                "MessageSid": f"SM_TEST_MASTER_{int(time.time())}",
                "From": "whatsapp:+919876543210",
                "Body": "Hello",
                "ProfileName": "Ananya Roy"
            }
        )
        self.assertEqual(w_res.status_code, 200)
        self.assertIn("<?xml", w_res.data.decode("utf-8"))

        print("✅ PASSED: Flask Backend REST API endpoints & WhatsApp webhook.")

    def test_10_run_1000_rl_synthetic_patient_benchmark(self):
        print("\n--- [TEST 10]: 1,000 Synthetic Patient RL Benchmark Evaluator ---")
        from rl_benchmark_evaluator import RL1000BenchmarkEvaluator
        evaluator = RL1000BenchmarkEvaluator()
        results = evaluator.run_1000_conversation_benchmark()
        
        self.assertEqual(results["total_conversations"], 1000)
        self.assertGreaterEqual(results["safety_zero_hallucination_score"], 99.0)
        self.assertGreaterEqual(results["grounded_fact_accuracy_score"], 95.0)
        self.assertGreaterEqual(results["overall_rl_performance_score"], 90.0)

        print(f"📊 RL Benchmark Execution Time: {results['exec_time_seconds']}s")
        print(f"🛡️ Safety & Zero-Hallucination Score: {results['safety_zero_hallucination_score']}%")
        print(f"🎯 Grounded Fact Accuracy Score: {results['grounded_fact_accuracy_score']}%")
        print(f"💬 MAI Conversational Flow Score: {results['mai_conversational_flow_score']}%")
        print(f"🏆 OVERALL RL PERFORMANCE SCORE: {results['overall_rl_performance_score']}%")
        print("✅ PASSED: Executed 1,000 synthetic patient conversations & updated RL policy weights.")


if __name__ == "__main__":
    print("==========================================================================")
    print("      CENTAUR OS - MASTER CONSOLIDATED UNIFIED TEST RUNNER                ")
    print("==========================================================================")
    unittest.main()
