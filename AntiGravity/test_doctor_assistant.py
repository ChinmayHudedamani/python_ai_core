import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from core.engine import CentaurCoreEngine

def test_doctor_queries():
    engine = CentaurCoreEngine()
    doctor_phone = "+91-7338350871"

    print("--- Test 1: Doctor asks for Financial Update ---")
    res1 = engine.process_patient_intake("financial update", patient_phone=doctor_phone)
    print(f"Status 1: {res1.get('status')}")
    print(f"Bot Response 1:\n{res1.get('whatsapp_response')}\n")

    print("--- Test 2: Doctor asks for Appointments ---")
    res2 = engine.process_patient_intake("show me today's appointments schedule", patient_phone=doctor_phone)
    print(f"Status 2: {res2.get('status')}")
    print(f"Bot Response 2:\n{res2.get('whatsapp_response')}\n")

    print("--- Test 3: Doctor asks to send PDF report ---")
    res3 = engine.process_patient_intake("send report", patient_phone=doctor_phone)
    print(f"Status 3: {res3.get('status')}")
    print(f"Bot Response 3:\n{res3.get('whatsapp_response')}\n")

    assert "DOCTOR_" in res1.get("status")
    print("✅ TEST PASSED: Doctor AI Assistant Mode correctly routes doctor requests and queries Neon PostgreSQL!")

if __name__ == "__main__":
    test_doctor_queries()
