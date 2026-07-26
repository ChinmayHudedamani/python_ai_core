import time
from typing import Dict, Any
from core.intent_classifier import ScikitLearnMLIntentEngine
from core.rate_limiter import TokenBucketRateLimiter, SlotConcurrencyLockManager
from core.conversation_store import ConversationSessionStore
from clinical.rag_generator import generate_zero_hallucination_response
from clinical.ledger_writer import OfflineLedgerWriter


class CentaurCoreEngine:
    """Unified Centaur OS Core AI Engine Coordinator."""

    def __init__(self):
        self.intent_ml = ScikitLearnMLIntentEngine()
        self.rate_limiter = TokenBucketRateLimiter(max_requests=5, window_seconds=60)
        self.lock_mgr = SlotConcurrencyLockManager(ttl_seconds=600)
        self.conv_store = ConversationSessionStore(max_turns=8)
        self.ledger = OfflineLedgerWriter()

    def process_patient_intake(self, raw_notes: str, patient_name: str = "Patient", patient_phone: str = "+91-9988776655", send_dispatch: bool = False) -> Dict[str, Any]:
        start_ts = time.time()
        clean_msg = raw_notes.strip().lower()

        # 0. Check Confirmation / Booking Intent ("1", "yes", "confirm")
        if clean_msg in ["1", "yes", "confirm", "confirm booking", "book slot"]:
            slot_id, is_locked, lock_msg = self.lock_mgr.reserve_slot(patient_phone, "GENERAL", 10, 0)
            ledger_res = self.ledger.write_appointment_lead(
                name=patient_name,
                phone=patient_phone,
                procedure_code="GENERAL",
                raw_notes=f"Confirmed Appointment (Slot {slot_id})"
            )
            self.conv_store.reset_session(patient_phone)
            confirm_reply = (
                f"Wonderful! I have reserved your appointment slot with Dr. Chinmay Hudedamani at Apex Dental Center, Koramangala. 😊\n\n"
                f"📋 Booking Reference: {slot_id}\n"
                f"📍 Location: 100 Feet Road, Koramangala, Bengaluru\n"
                f"📞 Direct Desk: +91-9988776655\n\n"
                f"We look forward to welcoming you! If you need to change your timing or ask any questions before coming, just message me here."
            )
            return {
                "status": "APPOINTMENT_CONFIRMED",
                "exec_ms": round((time.time() - start_ts) * 1000, 2),
                "whatsapp_response": confirm_reply,
                "ledger_result": ledger_res
            }

        # 0b. Direct Greeting Check
        if clean_msg in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "namaste", "hi there", "hello there"]:
            self.conv_store.reset_session(patient_phone)
            return {
                "status": "GREETING",
                "exec_ms": round((time.time() - start_ts) * 1000, 2),
                "whatsapp_response": "Thank you for contacting Apex Dental Center. How may I help you today?"
            }

        # 1. Rate Limit Inspection
        is_limited, limit_msg = self.rate_limiter.is_rate_limited(patient_phone)
        if is_limited:
            return {
                "status": "RATE_LIMITED",
                "whatsapp_response": limit_msg
            }

        # 2. Check 8-Turn Limit
        exceeded, handoff_data = self.conv_store.check_turn_limit_exceeded(patient_phone, raw_notes)
        if exceeded:
            return handoff_data

        # 3. Classify Intent via ML Classifier
        intent, confidence = self.intent_ml.classify(raw_notes)

        # 4. Generate Grounded Clinical Response
        patient_payload = {"notes": raw_notes, "name": patient_name, "phone": patient_phone}
        rag_result = generate_zero_hallucination_response(patient_payload)

        # 5. Append Turn to Session Store
        self.conv_store.append_chat_turn(patient_phone, raw_notes, rag_result)

        return {
            "status": "PROCESSED_SUCCESSFULLY",
            "exec_ms": round((time.time() - start_ts) * 1000, 2),
            "intent": intent,
            "confidence": confidence,
            "whatsapp_response": rag_result.get("whatsapp_response", "")
        }
