import json
import sys
import time
import datetime
from pathlib import Path
from day2_python import clean_client_data, mask_pii, validate_indian_phone_number, is_gibberish_text
from day6_python import SafetyCircuitBreaker
from day5_python import OfflineLedgerWriter
from conversation_store import ConversationSessionStore

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def print_header_banner():
    print("\n" + "=" * 65)
    print(" 🏥 LEVEL 9.5 CLINIC CENTAUR - MULTI-TURN AI CHAT DEMO 🏥")
    print(" Target Market: Private Dental Clinics & Implant Centers (Bengaluru)")
    print(" Feature: Multi-Turn Conversation Memory & Persistent Transcript Audit")
    print("=" * 65 + "\n")


def format_legible_patient_reply(whatsapp_text: str) -> str:
    """Formats bot response text for maximum legibility and visual clarity."""
    lines = whatsapp_text.splitlines()
    formatted_lines = []
    for line in lines:
        if line.startswith("🦷") or line.startswith("📋") or line.startswith("👨‍⚕️") or line.startswith("📍") or line.startswith("🕒") or line.startswith("📅") or line.startswith("⭐") or line.startswith("🚨") or line.startswith("⚠️"):
            formatted_lines.append(f"\n{line}")
        else:
            formatted_lines.append(line)
    return "\n".join(formatted_lines)


def run_interactive_multi_turn_demo():
    print_header_banner()
    breaker = SafetyCircuitBreaker()
    ledger = OfflineLedgerWriter()
    conv_store = ConversationSessionStore()

    print("Select Demo Option:")
    print("1. Start Multi-Turn Interactive Patient Session (Type live follow-ups)")
    print("2. Run Preset Case A: High-Ticket Invisalign Lead (Ananya Roy)")
    print("3. Run Preset Case B: Hinglish Dental Implant Lead (Rohan Verma)")
    print("4. Run Preset Case C: Medical Emergency ESI RED (Rajesh Hegde)")
    print("5. View Stored Patient Conversation History Transcripts")

    choice = input("\nEnter choice (1-5) [Default 1]: ").strip() or "1"

    if choice == "5":
        master_file = conv_store.master_path
        if master_file.exists():
            with open(master_file, "r", encoding="utf-8") as f:
                print("\n--- MASTER STORED CONVERSATIONS INDEX ---")
                print(json.dumps(json.load(f), indent=2))
        else:
            print("\nNo stored conversation history found yet.")
        return

    # Setup Initial Intake
    if choice == "2":
        name = "Ananya Roy"
        phone = "+91-9988776655"
        code = "ALIGNERS"
        initial_notes = "Hi, what is the cost of invislin clear aligners in Bengaluru? Do you have EMI options?"
    elif choice == "3":
        name = "Rohan Verma"
        phone = "+91-9876511223"
        code = "IMPLANTS"
        initial_notes = "Mera daant me bohot dard hai, dental implants ka kitna kharcha aayega?"
    elif choice == "4":
        name = "Rajesh Hegde"
        phone = "+91-9900011122"
        code = "EMERGENCY"
        initial_notes = "Patient fell down, profuse bleeding and unconscious. Urgent emergency!"
    else:
        print("\n--- NEW PATIENT REGISTRATION ---")
        name = input("Patient Name [e.g. Ananya Roy]: ").strip() or "Ananya Roy"

        # Enforce 10-Digit Indian Phone Validation
        while True:
            raw_phone = input("Phone Number (10-digit Indian Mobile e.g. +91-9988776655): ").strip() or "+91-9988776655"
            is_valid_phone, phone_msg = validate_indian_phone_number(raw_phone)
            if is_valid_phone:
                phone = phone_msg
                break
            else:
                print(f"⚠️ {phone_msg} Please enter a valid 10-digit Indian phone number.")

        code = input("Procedure Code [e.g. ALIGNERS / IMPLANTS / RCT]: ").strip() or "ALIGNERS"
        initial_notes = input("Inquiry Message: ").strip() or "What is the price of Invisalign clear aligners?"

    current_notes = initial_notes
    turn_counter = 0

    print(f"\n💬 STARTING PERSISTENT CHAT SESSION FOR {name.upper()} ({mask_pii(phone)})")
    print("Type your message below. Type 'exit', 'quit', or 'done' to finish session.\n")

    while True:
        turn_counter += 1
        print("=" * 65)
        print(f"📩 [TURN {turn_counter}] PATIENT MESSAGE: \"{current_notes}\"")
        print("=" * 65)

        # Check Turn Limit Safety Circuit (> 8 turns triggers Receptionist Handoff)
        exceeded, handoff_data = conv_store.check_turn_limit_exceeded(phone)
        if exceeded:
            print("\n🚨 SAFETY CIRCUIT TRIGGERED: MAXIMUM AUTOMATED FOLLOW-UP LIMIT EXCEEDED (>8 TURNS)")
            print(f"🔒 Session Flagged As    : RECEPTIONIST_REQUIRED")
            print(f"💾 Conversation Frozen At: {handoff_data['session_file']}")
            print("\n" + "📱 BOT WHATSAPP HANDOFF REPLY ".center(65, "─"))
            print(format_legible_patient_reply(handoff_data["whatsapp_response"]))
            print("─" * 65)
            print("\n❌ AUTOMATED BOT CONVERSATION HALTED. PATIENT TRANSFERRED TO HUMAN RECEPTIONIST.")
            break

        raw_intake = {
            "name": name,
            "phone": phone,
            "procedure_code": code,
            "notes": current_notes
        }

        start_time = time.time()
        result = breaker.process_intake_safety_circuit(raw_intake, is_followup=(turn_counter > 1))
        exec_ms = round((time.time() - start_time) * 1000, 2)

        triage = result.get("triage", {})
        circuit = result.get("circuit_status", {})
        grounding = result.get("grounding_facts", {})
        reply_text = result.get("whatsapp_response", "")

        # Save to Persistent Conversation Store
        save_status = conv_store.append_chat_turn(phone, current_notes, result)

        if save_status.get("status") == "RECEPTIONIST_REQUIRED_LIMIT_EXCEEDED":
            print("\n🚨 MAXIMUM FOLLOW-UP QUESTION LIMIT REACHED (8 TURNS). HALTING AUTOMATED BOT.")
            print(format_legible_patient_reply(save_status["whatsapp_response"]))
            break

        print(f"\n⚡ Processing Time: {exec_ms} ms | Triage Tier: {triage.get('lead_tier')} | Score: {triage.get('intent_score')}/100")
        print(f"🔒 Security & Safety Action: {circuit.get('circuit_action')}")
        print(f"💾 Transcript Saved To    : {save_status['session_file']}")

        print("\n" + "📱 BOT WHATSAPP REPLY ".center(65, "─"))
        print(format_legible_patient_reply(reply_text))
        print("─" * 65)

        # Allow Follow-Up Question Loop
        print("\n👇 ASK A FOLLOW-UP QUESTION (or type 'exit' to end session):")
        next_input = input("Follow-up Message > ").strip()

        if not next_input or next_input.lower() in ["exit", "quit", "done", "no", "bye"]:
            print(f"\n✅ CHAT SESSION ENDED FOR {name}. All {turn_counter} turns saved to conversation store.")
            break
        else:
            current_notes = next_input

    # Display Daily Executive Summary
    summary = ledger.generate_daily_summary()
    print("\n📊 LIVE CLINIC DAILY PIPELINE SUMMARY:")
    print(f"   • Total Leads Logged Today : {summary.get('total_records')}")
    print(f"   • Captured Pipeline Revenue: {summary.get('formatted_revenue')}")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    run_interactive_multi_turn_demo()
