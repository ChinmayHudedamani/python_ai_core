# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI / Centaur OS - Interactive Terminal CLI Demo Runner
# Created & Patented by Chinmay Hudedamani.

import sys
import io
import time
import random

# Force UTF-8 encoding for clean terminal emoji output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from core.engine import CentaurCoreEngine

def run_interactive_terminal_demo():
    print("\n" + "═" * 65)
    print(" 🦷 APEX AI — CLINICAL ASSISTANT INTERACTIVE TERMINAL DEMO 🦷")
    print("   Created & Patented by Chinmay Hudedamani | Apex Dental Center")
    print("═" * 65)
    print(" Type your message below to chat with APEX AI.")
    print(" Type 'reset' to restart session | Type 'exit' to quit.\n")

    engine = CentaurCoreEngine()
    session_phone = f"+91-9{random.randint(100000000, 999999999)}"
    patient_name = "Patient"

    # Initial Welcome Message
    print("🤖 APEX AI > Hey there! 👋 I'm APEX AI, your clinical assistant from Apex Dental Center & Implant Institute, Koramangala. 🌿")
    print("🤖 APEX AI > I'm here to guide you, answer your health questions, and connect you to care when needed.\n")
    print("🤖 APEX AI > To start, may I know your name?\n")

    while True:
        try:
            user_input = input("💬 Patient > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Exiting APEX AI Terminal Demo. Goodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ["exit", "quit", "q"]:
            print("\n👋 Thank you for using APEX AI Terminal Demo. Goodbye!")
            break

        if user_input.lower() == "reset":
            session_phone = f"+91-9{random.randint(100000000, 999999999)}"
            engine.conv_store.reset_session(session_phone)
            patient_name = "Patient"
            print("\n🔄 Session reset! Starting fresh conversation with APEX AI.\n")
            print("🤖 APEX AI > Hey there! 👋 I'm APEX AI, your clinical assistant from Apex Dental Center. May I know your name?\n")
            continue

        # Process message via Core AI Engine
        res = engine.process_patient_intake(
            raw_notes=user_input,
            patient_name=patient_name,
            patient_phone=session_phone
        )

        whatsapp_reply = res.get("whatsapp_response", "")
        exec_ms = res.get("exec_ms", 0)

        print(f"\n🤖 APEX AI ({exec_ms}ms) >\n{whatsapp_reply}\n")
        print("-" * 65 + "\n")

if __name__ == "__main__":
    run_interactive_terminal_demo()
