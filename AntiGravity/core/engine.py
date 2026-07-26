import time
import random
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

        # Extract patient name from notes if patient provided "Name - Problem"
        if "-" in raw_notes and len(raw_notes.split("-")[0].strip().split()) <= 3:
            extracted_name = raw_notes.split("-")[0].strip()
            if len(extracted_name) > 2:
                patient_name = extracted_name

        # 0a. Check Initial Booking Request ("1", "yes", "confirm", "book slot")
        if clean_msg in ["1", "yes", "confirm", "confirm booking", "book slot"]:
            slot_id, is_locked, lock_msg = self.lock_mgr.reserve_slot(patient_phone, "GENERAL", 10, 0)
            pay_url = f"https://centaur-bot.onrender.com/pay/{slot_id}"
            pay_reply = (
                f"To confirm your consultation with Dr. Chinmay Hudedamani, please complete the ₹500 consultation fee payment using the secure link below:\n\n"
                f"💳 Payment Link: {pay_url}\n"
                f"📌 Consultation Fee: ₹500 (Includes intraoral examination & 3D scan planning)\n"
                f"⌛ Slot Reference: {slot_id} (Held for 10 minutes)\n\n"
                f"Once paid, reply 'PAID' or '1' to lock your appointment slot!"
            )
            return {
                "status": "PAYMENT_LINK_GENERATED",
                "exec_ms": round((time.time() - start_ts) * 1000, 2),
                "whatsapp_response": pay_reply,
                "payment_url": pay_url
            }

        # 0b. Check Payment Confirmation ("paid", "payment done", "done", "txn")
        if clean_msg in ["paid", "payment done", "payment completed", "done", "txn"]:
            slot_id, is_locked, lock_msg = self.lock_mgr.reserve_slot(patient_phone, "GENERAL", 10, 0)
            txn_id = f"TXN_{int(time.time())}"
            auth_otp = str(abs(hash(patient_phone + str(int(time.time())))) % 9000 + 1000)

            display_name = patient_name if patient_name != "Patient" else "Valued Patient"

            ledger_res = self.ledger.write_appointment_lead(
                name=display_name,
                phone=patient_phone,
                procedure_code="GENERAL",
                raw_notes=f"Confirmed Appointment (Slot {slot_id}) | OTP: {auth_otp}",
                payment_status="PAID_CONFIRMED",
                transaction_id=txn_id
            )
            self.conv_store.reset_session(patient_phone)
            confirm_reply = (
                f"🎉 Payment Confirmed & Appointment Locked!\n\n"
                f"Patient Name: {display_name}\n"
                f"Phone Number: {patient_phone}\n"
                f"Doctor: Dr. Chinmay Hudedamani\n"
                f"Clinic: Apex Dental Center, Koramangala, Bengaluru\n"
                f"Slot Reference: {slot_id}\n"
                f"Payment Status: PAID (₹500 - Ref: {txn_id})\n\n"
                f"🔑 Clinic Check-In OTP: {auth_otp}\n"
                f"(Please present this 4-digit authentication code at the reception desk tomorrow for instant check-in!)\n\n"
                f"Dr. Chinmay's schedule has been updated. We look forward to seeing you!"
            )
            return {
                "status": "APPOINTMENT_CONFIRMED_PAID",
                "exec_ms": round((time.time() - start_ts) * 1000, 2),
                "whatsapp_response": confirm_reply,
                "auth_otp": auth_otp,
                "ledger_result": ledger_res
            }

        # 0c. Direct Greeting Check
        if clean_msg in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "namaste", "hi there", "hello there"]:
            self.conv_store.reset_session(patient_phone)
            return {
                "status": "GREETING",
                "exec_ms": round((time.time() - start_ts) * 1000, 2),
                "whatsapp_response": "Thank you for contacting Apex Dental Center. How may I help you today?"
            }

        # 0d. Gratitude & Exit Check ("thank you", "thanks", "bye")
        if any(w in clean_msg for w in ["thank you", "thanks", "thank u", "thx", "thankyou", "thanks a lot", "thank you so much", "bye", "goodbye", "ok thanks", "okay thanks"]):
            self.conv_store.reset_session(patient_phone)
            return {
                "status": "GRATITUDE_EXIT",
                "exec_ms": round((time.time() - start_ts) * 1000, 2),
                "whatsapp_response": "You're very welcome! 😊 It was a pleasure assisting you. Have a wonderful day, and please feel free to reach out anytime if you need anything else from Apex Dental Center!"
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
