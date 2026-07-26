import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from core.engine import CentaurCoreEngine

def test_anti_repetition_guard():
    engine = CentaurCoreEngine()
    test_phone = "+91-9876598765"

    print("--- Test 1: User sends ambiguous keyword 'something' ---")
    res1 = engine.process_patient_intake("something", patient_phone=test_phone)
    reply1 = res1.get("whatsapp_response", "")
    print(f"Reply 1:\n{reply1}\n")

    assert "overview of what we offer" in reply1.lower()

    print("--- Test 2: User sends the exact same keyword 'something' again ---")
    res2 = engine.process_patient_intake("something", patient_phone=test_phone)
    reply2 = res2.get("whatsapp_response", "")
    print(f"Reply 2:\n{reply2}\n")

    assert "without repeating information" in reply2.lower()
    assert reply1 != reply2

    print("✅ TEST PASSED: Anti-repetition guard prevents duplicate messages and presents grounded facts!")

if __name__ == "__main__":
    test_anti_repetition_guard()
