import os
import sys

# Ensure current directory is in sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from core.engine import CentaurCoreEngine


def start_patient_chat():
    print("==========================================================")
    print("       APEX DENTAL CENTER - PATIENT AI CHATBOT            ")
    print("==========================================================")
    print("Welcome! Ask any question about treatments, pricing, or appointments.")
    print("Type 'exit' or 'quit' to end the chat.\n")

    engine = CentaurCoreEngine()
    patient_name = "Patient"
    patient_phone = "+91-9988776655"

    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("\nAI: Thank you for visiting Apex Dental Center! Have a great day!")
                break

            result = engine.process_patient_intake(
                raw_notes=user_input,
                patient_name=patient_name,
                patient_phone=patient_phone,
                send_dispatch=False
            )

            reply = result.get("whatsapp_response", "")
            print(f"\nAI: {reply}\n")
            print("-" * 58)

        except (KeyboardInterrupt, EOFError):
            print("\nAI: Session ended. Goodbye!")
            break


if __name__ == "__main__":
    start_patient_chat()
