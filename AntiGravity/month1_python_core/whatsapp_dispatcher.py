import json
import datetime
from pathlib import Path
from typing import Dict, Any, List
from day2_python import mask_pii
from day6_python import SafetyCircuitBreaker
from day5_python import OfflineLedgerWriter

DOCTOR_PHONE_NUMBER: str = "+91-9988776600"  # Doctor / Clinic AE phone number

class WhatsAppChannelDispatcher:
    """
    Production-Ready WhatsApp Messaging & Doctor Dispatch Engine.
    Simulates Twilio / Meta WhatsApp Business API webhook payloads:
    1. Sends automated Zero-Hallucination WhatsApp reply to the PATIENT.
    2. Sends instant VIP Lead Alert Push Notification to the DOCTOR'S phone.
    3. Sends Daily Pipeline Ledger Summary to the DOCTOR'S phone.
    """

    def __init__(self, doctor_phone: str = DOCTOR_PHONE_NUMBER):
        self.doctor_phone: str = doctor_phone
        self.breaker: SafetyCircuitBreaker = SafetyCircuitBreaker()
        self.ledger: OfflineLedgerWriter = OfflineLedgerWriter()

    def build_meta_whatsapp_patient_payload(self, patient_phone: str, message_body: str) -> Dict[str, Any]:
        """Formats outbound WhatsApp message payload according to Meta WhatsApp Cloud API schema."""
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": patient_phone.replace("-", "").replace(" ", ""),
            "type": "text",
            "text": {"preview_url": True, "body": message_body}
        }

    def build_doctor_vip_notification(self, intake_result: Dict[str, Any]) -> Dict[str, Any]:
        """Formats high-priority notification payload for the DOCTOR'S personal WhatsApp number."""
        patient = intake_result.get("patient", {})
        triage = intake_result.get("triage", {})
        grounding = intake_result.get("grounding_facts", {})
        circuit = intake_result.get("circuit_status", {})

        doctors = grounding.get("matched_doctors", ["Dr. Chinmay Hudedamani"])
        slots = grounding.get("available_slots", [])
        primary_slot = slots[0] if slots else "PENDING_CONSULTATION"

        doc_message = (
            f"🔔 *NEW VIP HIGH-REVENUE LEAD ALERT* 🔔\n\n"
            f"👤 **Patient**: {patient.get('name')} ({patient.get('phone')})\n"
            f"🦷 **Procedure**: {patient.get('procedure_code')}\n"
            f"🎯 **Intent Score**: {triage.get('intent_score')}/100 ({triage.get('lead_tier')})\n"
            f"👨‍⚕️ **Assigned Doctor**: {doctors[0] if doctors else 'Dr. Chinmay'}\n"
            f"📅 **Reserved Slot**: {primary_slot}\n"
            f"⏱️ **Callback SLA**: {circuit.get('callback_window')}\n\n"
            f"💬 *Patient Message*: \"{patient.get('raw_notes', patient.get('notes'))}\""
        )

        return self.build_meta_whatsapp_patient_payload(self.doctor_phone, doc_message)

    def build_doctor_daily_ledger_report(self) -> Dict[str, Any]:
        """Compiles daily CSV ledger analytics into an executive WhatsApp report for the DOCTOR."""
        summary = self.ledger.generate_daily_summary()
        breakdown = summary.get("tier_breakdown", {})
        
        report_msg = (
            f"📊 *DAILY CLINIC PIPELINE LEDGER REPORT* 📊\n"
            f"🗓️ Date: {datetime.datetime.now().strftime('%A, %b %d, %Y')}\n\n"
            f"📈 **Total Leads Captured Today**: {summary.get('total_records')}\n"
            f"💰 **Captured Pipeline Revenue**: {summary.get('formatted_revenue')}\n\n"
            f"📌 **Lead Tiers Breakdown**:\n"
            f"  • VIP High-Revenue Leads : {breakdown.get('VIP_HIGH_REVENUE', 0)}\n"
            f"  • Emergency 112 Referrals: {breakdown.get('RED_CRITICAL_EMERGENCY', 0)}\n"
            f"  • Disqualified / Opt-outs : {breakdown.get('DISQUALIFIED', 0)}\n\n"
            f"📁 Master Ledger updated: `appointments_ledger.csv`"
        )
        return self.build_meta_whatsapp_patient_payload(self.doctor_phone, report_msg)

    def process_and_dispatch(self, raw_patient_intake: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes Full End-to-End Dispatch:
        - Evaluates safety circuit & RAG response
        - Generates Patient WhatsApp Payload
        - Generates Doctor Push Notification Payload (if VIP or Emergency)
        - Logs to Offline Ledger
        """
        result = self.breaker.process_intake_safety_circuit(raw_patient_intake)
        patient_phone = result.get("patient", {}).get("phone", "")
        patient_reply = result.get("whatsapp_response", "")
        triage = result.get("triage", {})

        # 1. Patient Payload
        patient_payload = self.build_meta_whatsapp_patient_payload(patient_phone, patient_reply)

        # 2. Doctor Alert Payload
        doctor_payload = None
        if triage.get("lead_tier") in ["VIP_HIGH_REVENUE", "RED_CRITICAL_EMERGENCY"]:
            doctor_payload = self.build_doctor_vip_notification(result)

        return {
            "status": "DISPATCH_READY",
            "patient_whatsapp_payload": patient_payload,
            "doctor_push_payload": doctor_payload,
            "circuit_status": result.get("circuit_status"),
            "ledger_result": result.get("ledger_result")
        }


if __name__ == "__main__":
    print("==================================================")
    print("   WHATSAPP MESSAGING & DOCTOR DISPATCH DEMO")
    print("==================================================\n")

    dispatcher = WhatsAppChannelDispatcher()

    sample_intake = {
        "name": "Ananya Roy",
        "phone": "+91-99887 76655",
        "procedure_code": "ALIGNERS",
        "notes": "Hi, what is the cost of invislin clear aligners in Bengaluru? Do you have EMI options?"
    }

    dispatch_res = dispatcher.process_and_dispatch(sample_intake)
    print(json.dumps(dispatch_res, indent=2))
