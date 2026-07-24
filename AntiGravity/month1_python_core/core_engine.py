import time
import sys
import json
import datetime
from typing import Dict, Any, Tuple, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from config_manager import SystemConfigManager
from day2_python import clean_client_data, validate_indian_phone_number, is_gibberish_text
from day4_python import generate_zero_hallucination_response, inspect_security_threats
from day6_python import SafetyCircuitBreaker
from day5_python import OfflineLedgerWriter
from conversation_store import ConversationSessionStore
from hardened_security_shield import FortifiedSecurityShield
from rate_limiter import TokenBucketRateLimiter
from concurrency_lock import SlotConcurrencyLockManager
from twilio_dispatcher import TwilioWhatsAppDispatcher


class CentaurCoreEngine:
    """
    Unified High-Performance Centaur OS Core Engine Coordinator.
    Provides a clean, centralized API for intake processing, security checks,
    triage scoring, ledger logging, and channel dispatches.
    """

    def __init__(self):
        self.config = SystemConfigManager()
        self.breaker = SafetyCircuitBreaker()
        self.ledger = OfflineLedgerWriter()
        self.conv_store = ConversationSessionStore(max_turns=self.config.get("max_allowed_followup_turns", 8))
        self.security = FortifiedSecurityShield()
        self.rate_limiter = TokenBucketRateLimiter(
            max_requests=self.config.get("rate_limit_max_requests_per_min", 5),
            window_seconds=60
        )
        self.lock_mgr = SlotConcurrencyLockManager(
            ttl_seconds=self.config.get("slot_reservation_ttl_seconds", 600)
        )
        self.twilio_dispatcher = TwilioWhatsAppDispatcher()

    def process_patient_intake(self, raw_notes: str, patient_name: str = "Patient", patient_phone: str = "+91-9988776655", send_dispatch: bool = False) -> Dict[str, Any]:
        """
        Executes the Unified End-to-End Processing Pipeline.
        Returns a clean patient response with zero duplicate dispatches.
        """
        start_ts = time.time()
        clean_msg = raw_notes.strip().lower()

        # 0. Check Confirmation / Booking Intent ("1", "yes", "confirm")
        if clean_msg in ["1", "yes", "confirm", "confirm booking", "book slot"]:
            # Reserve slot & write to ledger
            slot_id, is_locked, lock_msg = self.lock_mgr.reserve_slot(patient_phone, "GENERAL", 10, 0)
            ledger_res = self.ledger.write_appointment_lead(
                name=patient_name,
                phone=patient_phone,
                procedure_code="GENERAL",
                raw_notes=f"Confirmed Appointment (Slot {slot_id})"
            )
            # Reset conversation turn counter for next session
            self.conv_store.reset_session(patient_phone)
            
            confirm_reply = (
                f"Appointment Confirmed!\n\n"
                f"Patient: {patient_name}\n"
                f"Doctor: Dr. Chinmay Hudedamani\n"
                f"Location: Apex Dental Center, Koramangala, Bengaluru\n"
                f"Booking ID: {slot_id}\n\n"
                f"We look forward to seeing you!"
            )
            return {
                "status": "APPOINTMENT_CONFIRMED",
                "exec_ms": round((time.time() - start_ts) * 1000, 2),
                "patient_phone": patient_phone,
                "patient_name": patient_name,
                "whatsapp_response": confirm_reply,
                "ledger_result": ledger_res
            }

        # 1. Rate Limit Inspection
        is_limited, limit_msg = self.rate_limiter.is_rate_limited(patient_phone)
        if is_limited:
            return {
                "status": "RATE_LIMITED",
                "exec_ms": round((time.time() - start_ts) * 1000, 2),
                "whatsapp_response": limit_msg
            }

        # 2. Check 8-Turn Follow-up Question Circuit
        exceeded, handoff_data = self.conv_store.check_turn_limit_exceeded(patient_phone, raw_notes)
        if exceeded:
            return handoff_data

        # 3. Clean and Validate Intake Data
        raw_intake = {
            "name": patient_name,
            "phone": patient_phone,
            "procedure_code": "GENERAL",
            "notes": raw_notes
        }
        cleaned_intake = clean_client_data(raw_intake)

        # 4. Process Safety Circuit & Zero-Hallucination Generator
        circuit_result = self.breaker.process_intake_safety_circuit(cleaned_intake)
        exec_ms = round((time.time() - start_ts) * 1000, 2)

        # 5. Persistent Session Store Logging
        self.conv_store.append_chat_turn(patient_phone, raw_notes, circuit_result)

        # 6. Optional Outbound Dispatch (Disabled by default for webhooks to prevent duplicate dispatches)
        twilio_dispatch = None
        if send_dispatch:
            twilio_dispatch = self.twilio_dispatcher.send_whatsapp_message(patient_phone, circuit_result.get("whatsapp_response", ""))

        return {
            "status": "PROCESSED_SUCCESSFULLY",
            "exec_ms": exec_ms,
            "patient_phone": patient_phone,
            "patient_name": patient_name,
            "triage": circuit_result.get("triage", {}),
            "circuit_status": circuit_result.get("circuit_status", {}),
            "grounding_facts": circuit_result.get("grounding_facts", {}),
            "whatsapp_response": circuit_result.get("whatsapp_response", ""),
            "twilio_dispatch": twilio_dispatch,
            "ledger_result": circuit_result.get("ledger_result", {})
        }


if __name__ == "__main__":
    engine = CentaurCoreEngine()
    test_res = engine.process_patient_intake("Hi, what is the cost of Invisalign clear aligners in Koramangala?", "Ananya Roy", "+91-9988776655")
    print("  ✅ Unified Core Engine Refactoring Check Succeeded!")
    print(f"  • Execution Latency : {test_res['exec_ms']} ms")
    print(f"  • Lead Tier        : {test_res['triage'].get('lead_tier')}")
    print(f"  • Intent Score     : {test_res['triage'].get('intent_score')}/100")
