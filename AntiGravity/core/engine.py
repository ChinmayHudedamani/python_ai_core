import os
import time
import random
import re
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
        self._verified_patients: Dict[str, Dict[str, str]] = {}
        self._pending_payment_links: set = set()

    def process_patient_intake(self, raw_notes: str, patient_name: str = "Patient", patient_phone: str = "+91-9988776655", send_dispatch: bool = False) -> Dict[str, Any]:
        start_ts = time.time()
        clean_msg = raw_notes.strip().lower()

        sender_phone = patient_phone

        # Doctor Role-Based Executive Assistant Routing
        doctor_target = os.getenv("DOCTOR_PHONE", "+91-7338350871").replace("+", "").replace("-", "").replace(" ", "").strip()
        clean_sender = sender_phone.replace("+", "").replace("-", "").replace(" ", "").strip()

        if clean_sender in [doctor_target, "7338350871", "917338350871"]:
            from core.doctor_assistant import process_doctor_executive_query
            res = process_doctor_executive_query(raw_notes, sender_phone)
            res["exec_ms"] = round((time.time() - start_ts) * 1000, 2)
            return res

        # Robust Patient Name & Contact Phone Extraction
        phone_match = re.search(r"(\+?\d{1,3}[\s-]?)?(\d{10}|\d{5}[\s-]\d{5})", raw_notes)
        
        # Insufficient Data Guard: Check if patient provided name but NO 10-digit phone number
        is_generic_word = clean_msg in ["hi", "hello", "hey", "help", "1", "yes", "confirm", "confirm booking", "book slot", "paid", "payment done", "done", "appointments", "financial update"]
        is_name_only = not phone_match and len(raw_notes.split()) <= 4 and not is_generic_word and any(w.isalpha() for w in clean_msg.split())

        if is_name_only:
            extracted_name = raw_notes.strip().title()
            return {
                "status": "INSUFFICIENT_DATA_MISSING_PHONE",
                "exec_ms": round((time.time() - start_ts) * 1000, 2),
                "whatsapp_response": (
                    f"⚠️ Data Insufficient!\n\n"
                    f"Thank you, {extracted_name}. We received your name, but your 10-digit contact mobile number is missing.\n\n"
                    f"Please reply with your 10-digit mobile number (e.g., '{extracted_name} - 9876543210' or '9876543210') so we can issue your consultation slot & appointment OTP!"
                )
            }

        if phone_match:
            extracted_phone = phone_match.group(0).strip()
            clean_for_name = raw_notes.replace(extracted_phone, "")
            clean_for_name = re.sub(
                r"\b(for|my|father|mother|son|daughter|wife|husband|friend|brother|sister|patient|name|is|phone|number|mobile|contact)\b",
                "",
                clean_for_name,
                flags=re.IGNORECASE
            )
            clean_for_name = clean_for_name.replace("-", "").replace(":", "").strip()
            words = [w for w in clean_for_name.split() if len(w) > 1 and w.isalpha()]
            if words:
                patient_name = " ".join(words[:3]).title()
            patient_phone = extracted_phone

            self._verified_patients[sender_phone] = {
                "name": patient_name,
                "phone": patient_phone
            }

            # If user provided Patient Name & Contact Phone during booking step
            if len(raw_notes.split()) <= 10:
                slot_id, is_locked, lock_msg = self.lock_mgr.reserve_slot(patient_phone, "GENERAL", 10, 0)
                pay_url = f"https://centaur-bot.onrender.com/pay/{slot_id}"
                self._pending_payment_links.add(sender_phone)
                self._pending_payment_links.add(patient_phone)
                pay_reply = (
                    f"Thank you! Booking registered for:\n"
                    f"👤 Patient Name: {patient_name}\n"
                    f"📞 Contact Phone: {patient_phone}\n\n"
                    f"To lock your consultation with Dr. Chinmay Hudedamani, please complete the ₹500 consultation fee payment using the secure link below:\n\n"
                    f"💳 Payment Link: {pay_url}\n"
                    f"📌 Consultation Fee: ₹500 (Includes intraoral examination & 3D scan planning)\n"
                    f"⌛ Slot Reference: {slot_id} (Held for 10 minutes)\n\n"
                    f"Once paid, reply 'PAID' or '1' to lock your appointment slot!"
                )
                return {
                    "status": "PATIENT_VERIFIED_PAYMENT_LINK_GENERATED",
                    "exec_ms": round((time.time() - start_ts) * 1000, 2),
                    "whatsapp_response": pay_reply,
                    "payment_url": pay_url
                }

        # Check if we have previously verified patient details for this sender
        if sender_phone in self._verified_patients:
            patient_name = self._verified_patients[sender_phone]["name"]
            patient_phone = self._verified_patients[sender_phone]["phone"]

        has_pending = sender_phone in self._pending_payment_links or patient_phone in self._pending_payment_links

        # 0a. Check Payment Confirmation ("paid", "1", "yes", "done", "confirm") when payment link is pending OR msg is explicit paid
        is_paid_msg = clean_msg in ["paid", "payment done", "payment completed", "done", "txn"]
        is_confirm_when_pending = has_pending and clean_msg in ["1", "yes", "confirm", "confirm booking", "lock", "pay"]

        if is_paid_msg or is_confirm_when_pending:
            slot_id, is_locked, lock_msg = self.lock_mgr.reserve_slot(patient_phone, "GENERAL", 10, 0)
            
            if not is_locked:
                return {
                    "status": "DOUBLE_BOOKING_PREVENTED",
                    "exec_ms": round((time.time() - start_ts) * 1000, 2),
                    "whatsapp_response": "⚠️ Apologies! That consultation slot was reserved by another patient. Please select another slot or reply '1' to check available timings!"
                }

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

            if ledger_res.get("status") == "DOUBLE_BOOKING_PREVENTED":
                return {
                    "status": "DOUBLE_BOOKING_PREVENTED",
                    "exec_ms": round((time.time() - start_ts) * 1000, 2),
                    "whatsapp_response": "⚠️ This slot has already been confirmed by another patient. Please choose a different time slot!"
                }

            self.conv_store.reset_session(sender_phone)
            self._pending_payment_links.discard(sender_phone)
            self._pending_payment_links.discard(patient_phone)
            if sender_phone in self._verified_patients:
                del self._verified_patients[sender_phone]

            confirm_reply = (
                f"🎉 Payment Confirmed & Appointment Locked!\n\n"
                f"Patient Name: {display_name}\n"
                f"Contact Phone: {patient_phone}\n"
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

        # 0b. Check Initial Booking Request ("1", "yes", "confirm", "book slot")
        if clean_msg in ["1", "yes", "confirm", "confirm booking", "book slot"]:
            slot_id, is_locked, lock_msg = self.lock_mgr.reserve_slot(patient_phone, "GENERAL", 10, 0)
            if not is_locked:
                return {
                    "status": "DOUBLE_BOOKING_PREVENTED",
                    "exec_ms": round((time.time() - start_ts) * 1000, 2),
                    "whatsapp_response": "⚠️ That consultation slot is currently held by another patient. Please select another time!"
                }
            pay_url = f"https://centaur-bot.onrender.com/pay/{slot_id}"
            self._pending_payment_links.add(sender_phone)
            self._pending_payment_links.add(patient_phone)
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

        # 0c. Direct Greeting Check
        if clean_msg in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "namaste", "hi there", "hello there"]:
            self.conv_store.reset_session(sender_phone)
            return {
                "status": "GREETING",
                "exec_ms": round((time.time() - start_ts) * 1000, 2),
                "whatsapp_response": "Thank you for contacting Apex Dental Center. How may I help you today?"
            }

        # 0d. Gratitude & Exit Check ("thank you", "thanks", "bye", "dhanyawad")
        if any(w in clean_msg for w in ["thank you", "thanks", "thank u", "thx", "thankyou", "thanks a lot", "thank you so much", "bye", "goodbye", "ok thanks", "okay thanks", "dhanyawad", "dhanyavad", "shukriya", "shukriyaa"]):
            self.conv_store.reset_session(sender_phone)
            return {
                "status": "GRATITUDE_EXIT",
                "exec_ms": round((time.time() - start_ts) * 1000, 2),
                "whatsapp_response": "You're very welcome! 😊 It was a pleasure assisting you. Have a wonderful day, and please feel free to reach out anytime if you need anything else from Apex Dental Center!"
            }

        # 1. Rate Limit Inspection
        is_limited, limit_msg = self.rate_limiter.is_rate_limited(sender_phone)
        if is_limited:
            return {
                "status": "RATE_LIMITED",
                "whatsapp_response": limit_msg
            }

        # 2. Check 8-Turn Limit
        exceeded, handoff_data = self.conv_store.check_turn_limit_exceeded(sender_phone, raw_notes)
        if exceeded:
            return handoff_data

        # 3. Classify Intent via ML Classifier
        intent, confidence = self.intent_ml.classify(raw_notes)

        # 4. Generate Grounded Clinical Response
        patient_payload = {"notes": raw_notes, "name": patient_name, "phone": patient_phone}
        rag_result = generate_zero_hallucination_response(patient_payload)

        # 5. Append Turn to Session Store
        self.conv_store.append_chat_turn(sender_phone, raw_notes, rag_result)

        return {
            "status": "PROCESSED_SUCCESSFULLY",
            "exec_ms": round((time.time() - start_ts) * 1000, 2),
            "intent": intent,
            "confidence": confidence,
            "whatsapp_response": rag_result.get("whatsapp_response", "")
        }
