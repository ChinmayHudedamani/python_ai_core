import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from core.engine import CentaurCoreEngine

def test_insufficient_data_handling():
    engine = CentaurCoreEngine()
    test_phone = "+91-9988112233"

    print("--- Test 1: User sends only name 'chinmay' ---")
    res1 = engine.process_patient_intake("chinmay", patient_phone=test_phone)
    print(f"Status 1: {res1.get('status')}")
    print(f"Bot Response 1:\n{res1.get('whatsapp_response')}\n")

    assert res1.get("status") == "INSUFFICIENT_DATA_MISSING_PHONE"
    assert "Data Insufficient" in res1.get("whatsapp_response")

    print("--- Test 2: User follows up with name and phone 'Chinmay - 7338350871' ---")
    res2 = engine.process_patient_intake("Chinmay - 7338350871", patient_phone=test_phone)
    print(f"Status 2: {res2.get('status')}")
    print(f"Bot Response 2:\n{res2.get('whatsapp_response')}\n")

    assert res2.get("status") == "PATIENT_VERIFIED_PAYMENT_LINK_GENERATED"
    print("✅ TEST PASSED: Name-only input triggers 'Data Insufficient' and prompts for mobile number!")

if __name__ == "__main__":
    test_insufficient_data_handling()
