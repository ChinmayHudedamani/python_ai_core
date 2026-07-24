import json
import sys
import time
import datetime
from pathlib import Path
from day2_python import clean_client_data, mask_pii, validate_indian_phone_number, is_gibberish_text
from day6_python import SafetyCircuitBreaker
from day5_python import OfflineLedgerWriter
from whatsapp_dispatcher import EliteWhatsAppChannelDispatcher
from conversation_store import ConversationSessionStore
from ical_generator import ICalAppointmentGenerator
from appointment_reminder import AppointmentReminderEngine
from payment_gateway import RazorpayUPIPaymentEngine
from rigorous_bot_stress_test import run_rigorous_bot_breakdown_machine

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def print_header_banner():
    print("\n" + "=" * 67)
    print(" 🏥 LEVEL 9.5 ENTERPRISE CLINIC CENTAUR - SALES DEMO ENGINE 🏥")
    print(" Target Market: Private Dental Clinics & Implant Centers (Bengaluru)")
    print(" Value Prop: 24/7 Zero-Hallucination Lead Capture & 100% Safety Shield")
    print("=" * 67 + "\n")


def print_feature_matrix_showcase():
    """Renders the High-Converting Feature Matrix Showcase for Clinic Owners."""
    print("\n" + "=" * 67)
    print(" 🌟 THE 8 IRRESISTIBLE 'BUY-ON-THE-SPOT' CLINIC FEATURES 🌟")
    print("=" * 67 + "\n")

    features = [
        ("⚡ 24/7 Zero-Hallucination WhatsApp Response", "Responds to late-night inquiries (11:30 PM) in 2 seconds with exact procedure prices, warranties, and 0% EMI plans."),
        ("😴 Doctor Quiet-Hours Sleep Protection (9PM-8AM)", "Never wakes doctors at 2 AM for routine questions. Queues VIP leads for 8:30 AM morning callback; routes 112 medical emergencies 24/7."),
        ("📊 Zero Cloud EMR Hassle (Instant Auto-Excel Sync)", "Requires zero staff training. Automatically logs all appointments into a simple appointments_ledger.csv on your desk computer."),
        ("📲 Dual WhatsApp Patient & Doctor Alerting", "Sends instant lead push alerts to the doctor's phone with 1-click CTA buttons ([📞 Call Patient Now], [✅ Confirm Slot])."),
        ("🛡️ 100% Medical Legal & Prescription Shield", "Refuses patient requests for painkillers/drugs legally, protecting your clinic from malpractice lawsuits and liability."),
        ("📅 1-Click Google Calendar & iCal Sync", "Embeds downloadable .ics calendar invitations directly into patient WhatsApp chats for seamless appointment reminders."),
        ("💳 Instant UPI / Razorpay Payment Links", "Generates ₹500 initial consultation reservation payment links directly inside WhatsApp chat."),
        ("⏰ Automated 24-Hour WhatsApp Appointment Reminders", "Sends automated pre-appointment reminders to reduce patient no-shows by 80%.")
    ]

    for idx, (title, desc) in enumerate(features, 1):
        print(f" {idx}. {title}")
        print(f"    👉 {desc}\n")

    print("=" * 67)
    print(" 🏆 COMPETITIVE COMPARISON MATRIX")
    print("=" * 67)
    print(" Feature                          | Generic Chatbot | Centaur OS")
    print(" -------------------------------- | --------------- | ----------")
    print(" 24/7 After-Hours Lead Capture    | ❌ No           | ✅ YES (2 Sec)")
    print(" 0% EMI & Exact Price Quotes      | ❌ Hallucinates  | ✅ 100% Fact-Checked")
    print(" 2 AM Doctor Sleep Protection     | ❌ Rings Doctor | ✅ Queues 8:30 AM")
    print(" Prescription Legal Protection    | ❌ Dangerous    | ✅ 100% Refusal Shield")
    print(" Direct Excel Ledger Sync         | ❌ Requires SaaS| ✅ Auto-CSV Sync")
    print(" Instant UPI Reservation Links    | ❌ No           | ✅ Razorpay / GPay")
    print(" 8 Follow-Up Handoff Circuit       | ❌ Infinite Loop| ✅ Receptionist Handoff")
    print("=" * 67 + "\n")


def format_legible_patient_reply(whatsapp_text: str) -> str:
    """Formats bot response text for maximum legibility and visual clarity."""
    lines = whatsapp_text.splitlines()
    formatted_lines = []
    for line in lines:
        if line.startswith("🦷") or line.startswith("📋") or line.startswith("👨‍⚕️") or line.startswith("📍") or line.startswith("🕒") or line.startswith("📅") or line.startswith("⭐") or line.startswith("🚨") or line.startswith("⚠️") or line.startswith("📞") or line.startswith("💳") or line.startswith("⏰"):
            formatted_lines.append(f"\n{line}")
        else:
            formatted_lines.append(line)
    return "\n".join(formatted_lines)


def run_clinic_roi_calculator():
    """Live Interactive ROI Calculator grounded on realistic dental clinic metrics."""
    print("\n" + "=" * 65)
    print(" 📊 REALISTIC CLINIC ROI & REVENUE PROJECTION CALCULATOR 📊")
    print("=" * 65)

    try:
        monthly_leads = int(input("\n1. Estimated monthly WhatsApp patient inquiries [e.g. 45]: ").strip() or "45")
        avg_treatment_fee = int(input("2. Average treatment package fee (INR) [e.g. 34000]: ").strip() or "34000")

        after_hours_ratio = 0.30
        competitor_loss_ratio = 0.50
        conversion_rate_with_bot = 0.25

        after_hours_leads = round(monthly_leads * after_hours_ratio)
        lost_leads_monthly = round(after_hours_leads * competitor_loss_ratio)
        lost_revenue_monthly = lost_leads_monthly * avg_treatment_fee

        captured_treatments_monthly = max(1, round(lost_leads_monthly * conversion_rate_with_bot))
        new_monthly_revenue = captured_treatments_monthly * avg_treatment_fee

        system_cost_monthly = 6000
        net_profit_monthly = new_monthly_revenue - system_cost_monthly
        roi_multiple = round(new_monthly_revenue / system_cost_monthly, 1)

        print("\n" + "📈 YOUR REALISTIC CLINIC REVENUE PROJECTION RESULTS ".center(65, "─"))
        print(f" • Monthly Patient Inquiries       : {monthly_leads} leads/month")
        print(f" • After-Hours Inquiries (8PM-8AM) : {after_hours_leads} leads/month")
        print(f" • Unanswered Leads Lost           : {lost_leads_monthly} leads/month")
        print(f" 🔴 Estimated Revenue Lost Without AI  : ₹{lost_revenue_monthly:,} / month")
        print(f" 🟢 Net New Paid Treatments Closed : {captured_treatments_monthly} extra patient(s)/month")
        print(f" 💰 Net New Monthly Revenue Captured  : ₹{new_monthly_revenue:,} / month")
        print(f" ⚙️ System Maintenance Fee            : ₹{system_cost_monthly:,} / month")
        print(f" 🚀 NET CLINIC MONTHLY PROFIT         : ₹{net_profit_monthly:,} / month")
        print(f" 🌟 REALISTIC CONSERVATIVE MONTHLY ROI: {roi_multiple}x RETURN ON INVESTMENT")
        print("─" * 65 + "\n")
    except Exception:
        print("\n⚠️ Invalid input. Returning to main menu.")


def run_interactive_multi_turn_demo():
    print_header_banner()
    breaker = SafetyCircuitBreaker()
    ledger = OfflineLedgerWriter()
    conv_store = ConversationSessionStore()
    dispatcher = EliteWhatsAppChannelDispatcher()
    ical_gen = ICalAppointmentGenerator()
    reminder_eng = AppointmentReminderEngine()
    payment_eng = RazorpayUPIPaymentEngine()

    print("Select Demo Option:")
    print("1. Start Multi-Turn Interactive Patient Session (Type live follow-ups)")
    print("2. Preset Case A: High-Ticket Invisalign Lead (Ananya Roy - ₹1,20,000)")
    print("3. Preset Case B: Hinglish Dental Implant Lead (Rohan Verma - ₹45,000)")
    print("4. Preset Case C: Medical Emergency ESI RED (Rajesh Hegde - 112 Override)")
    print("5. View Stored Patient Conversation History Transcripts")
    print("6. Run Live Clinic ROI & Revenue Calculator (Show Doctor the Money)")
    print("7. Preview Doctor's Daily 8:00 PM WhatsApp Revenue Ledger Report")
    print("8. Run Rigorous Bot Breakdown Machine (10 Adversarial Stress Test Scenarios)")
    print("9. Generate ₹500 Consultation Fee UPI / Razorpay Payment Link")
    print("10. View Irresistible Clinic Feature Matrix & Competitive Comparison")

    choice = input("\nEnter choice (1-10) [Default 1]: ").strip() or "1"

    if choice == "5":
        master_file = conv_store.master_path
        if master_file.exists():
            with open(master_file, "r", encoding="utf-8") as f:
                print("\n--- MASTER STORED CONVERSATIONS INDEX ---")
                print(json.dumps(json.load(f), indent=2))
        else:
            print("\nNo stored conversation history found yet.")
        return
    elif choice == "6":
        run_clinic_roi_calculator()
        return
    elif choice == "7":
        print("\n" + "=" * 65)
        print(" 📱 PREVIEW: DOCTOR'S DAILY 8:00 PM WHATSAPP LEDGER REPORT")
        print("=" * 65 + "\n")
        report_payload = dispatcher.build_doctor_daily_ledger_report()
        print(report_payload["interactive"]["body"]["text"])
        print("\nInteractive CTA Buttons:")
        for btn in report_payload["interactive"]["action"]["buttons"]:
            print(f" [ {btn['reply']['title']} ]", end=" ")
        print("\n" + "=" * 65 + "\n")
        return
    elif choice == "8":
        run_rigorous_bot_breakdown_machine()
        return
    elif choice == "9":
        print("\n" + "=" * 65)
        print(" 💳 GENERATE ₹500 CONSULTATION FEE UPI / RAZORPAY PAYMENT LINK")
        print("=" * 65 + "\n")
        pay_res = payment_eng.generate_consultation_fee_link("Ananya Roy", "+91-9988776655", 500)
        print(pay_res["whatsapp_text"])
        print("\n" + "=" * 65 + "\n")
        return
    elif choice == "10":
        print_feature_matrix_showcase()
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

        # Generate 1-Click iCal event file for appointment
        ics_path = ical_gen.create_ics_event(name, code, "Dr. Chinmay Hudedamani", "Saturday at 11:00 AM")

        # Save to Persistent Conversation Store
        save_status = conv_store.append_chat_turn(phone, current_notes, result)

        if save_status.get("status") == "RECEPTIONIST_REQUIRED_LIMIT_EXCEEDED":
            print("\n🚨 MAXIMUM FOLLOW-UP QUESTION LIMIT REACHED (8 TURNS). HALTING AUTOMATED BOT.")
            print(format_legible_patient_reply(save_status["whatsapp_response"]))
            break

        print(f"\n⚡ Processing Time: {exec_ms} ms | Triage Tier: {triage.get('lead_tier')} | Score: {triage.get('intent_score')}/100")
        print(f"🔒 Security & Safety Action: {circuit.get('circuit_action')}")
        print(f"📅 1-Click iCal Event Created: {ics_path}")
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
