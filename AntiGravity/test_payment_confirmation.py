import sys
import io

# Force UTF-8 stdout encoding for Windows PowerShell / CMD
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from core.engine import CentaurCoreEngine

def test_booking_flow():
    engine = CentaurCoreEngine()
    test_phone = "+91-9988771122"
    test_name = "Test Patient"

    print("Step 1: Patient requests booking...")
    res1 = engine.process_patient_intake(
        raw_notes=f"Hi I am {test_name} {test_phone}, I want to book an appointment",
        patient_name=test_name,
        patient_phone=test_phone
    )
    print(f"Status 1: {res1.get('status')}")

    print("Step 2: Patient replies '1' to confirm booking interest...")
    res2 = engine.process_patient_intake(
        raw_notes="1",
        patient_name=test_name,
        patient_phone=test_phone
    )
    print(f"Status 2: {res2.get('status')}")
    print(f"Bot Response 2:\n{res2.get('whatsapp_response')}\n")

    assert res2.get("status") == "PAYMENT_LINK_GENERATED", f"Expected PAYMENT_LINK_GENERATED but got {res2.get('status')}"

    print("Step 3: Patient replies '1' AFTER receiving payment link...")
    res3 = engine.process_patient_intake(
        raw_notes="1",
        patient_name=test_name,
        patient_phone=test_phone
    )
    print(f"Status 3: {res3.get('status')}")
    print(f"Bot Response 3:\n{res3.get('whatsapp_response')}\n")

    assert res3.get("status") == "APPOINTMENT_CONFIRMED_PAID", f"Expected APPOINTMENT_CONFIRMED_PAID but got {res3.get('status')}"
    print("✅ TEST PASSED SUCCESSFULLY: Replying '1' after payment link generation correctly locks the appointment and confirms payment!")

if __name__ == "__main__":
    test_booking_flow()
