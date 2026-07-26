import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from clinical.rag_generator import generate_zero_hallucination_response

def test_operating_hours():
    print("--- Test 1: User requests 10:30 PM (outside operating hours) ---")
    res1 = generate_zero_hallucination_response({"notes": "tm 10 30pm"})
    reply1 = res1.get("whatsapp_response", "")
    print(f"Reply 1:\n{reply1}\n")

    assert "outside our operating hours" in reply1.lower()
    assert "10:30 PM" in reply1

    print("--- Test 2: User requests 10:30 AM (valid operating hours) ---")
    res2 = generate_zero_hallucination_response({"notes": "tm 10 30am"})
    reply2 = res2.get("whatsapp_response", "")
    print(f"Reply 2:\n{reply2}\n")

    assert "hold that time for you" in reply2.lower()

    print("✅ TEST PASSED: Out-of-bounds clinic hours (10:30 PM) are properly declined and valid slots suggested!")

if __name__ == "__main__":
    test_operating_hours()
