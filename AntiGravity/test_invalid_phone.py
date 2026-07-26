import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from core.engine import CentaurCoreEngine

def test_invalid_phone_handling():
    engine = CentaurCoreEngine()
    test_phone = "+91-9988112233"

    print("--- Test 1: User enters short phone number 'Chinmay - 98765' ---")
    res1 = engine.process_patient_intake("Chinmay - 98765", patient_phone=test_phone)
    print(f"Status 1: {res1.get('status')}")
    print(f"Bot Response 1:\n{res1.get('whatsapp_response')}\n")

    assert res1.get("status") == "INVALID_PHONE_NUMBER"
    assert "Invalid Mobile Number" in res1.get("whatsapp_response")

    print("--- Test 2: User enters dummy phone number '0000000000' ---")
    res2 = engine.process_patient_intake("0000000000", patient_phone=test_phone)
    print(f"Status 2: {res2.get('status')}")
    print(f"Bot Response 2:\n{res2.get('whatsapp_response')}\n")

    assert res2.get("status") == "INVALID_PHONE_NUMBER"

    print("--- Test 3: User enters valid 10-digit phone number 'Chinmay - 7338350871' ---")
    res3 = engine.process_patient_intake("Chinmay - 7338350871", patient_phone=test_phone)
    print(f"Status 3: {res3.get('status')}")
    print(f"Bot Response 3:\n{res3.get('whatsapp_response')}\n")

    assert res3.get("status") == "PATIENT_VERIFIED_PAYMENT_LINK_GENERATED"

    print("✅ TEST PASSED: Invalid and short phone numbers are rejected with helpful guidance!")

if __name__ == "__main__":
    test_invalid_phone_handling()
