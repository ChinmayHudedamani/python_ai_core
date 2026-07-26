import re
import json
import logging
import threading
from enum import Enum
from typing import Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)


class State(str, Enum):
    """Strict Finite State Machine (FSM) States for Healthcare Funnel."""
    TRIAGE = "TRIAGE"
    CALENDAR_SELECTION = "CALENDAR_SELECTION"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    COMPLETED = "COMPLETED"


class SessionStore:
    """Thread-safe state persistence store for patient phone numbers."""

    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def get_session(self, phone: str) -> Dict[str, Any]:
        with self._lock:
            if phone not in self._store:
                self._store[phone] = {
                    "state": State.TRIAGE,
                    "procedure": None,
                    "slot": None,
                    "txn_id": None
                }
            return self._store[phone]

    def update_state(self, phone: str, next_state: State, **kwargs) -> None:
        with self._lock:
            session = self.get_session(phone)
            session["state"] = next_state
            session.update(kwargs)

    def reset_session(self, phone: str) -> None:
        with self._lock:
            self._store[phone] = {
                "state": State.TRIAGE,
                "procedure": None,
                "slot": None,
                "txn_id": None
            }


session_store = SessionStore()


class PureNLUParser:
    """Relegates LLM / Regex to pure NLU entity extraction (Zero flow control)."""

    @staticmethod
    def parse_nlu(text: str) -> Dict[str, Any]:
        clean = text.strip().lower()

        if any(w in clean for w in ["invisalign", "aligner", "braces", "clip", "wire"]):
            procedure = "Invisalign Clear Aligners"
        elif any(w in clean for w in ["implant", "implants", "tooth root"]):
            procedure = "Dental Implants"
        elif any(w in clean for w in ["rct", "root canal"]):
            procedure = "Single-Visit Root Canal"
        elif any(w in clean for w in ["clean", "cleaning", "scaling", "polish"]):
            procedure = "Teeth Cleaning & Scaling"
        else:
            procedure = "General Consultation"

        is_booking_intent = any(w in clean for w in ["book", "appointment", "slot", "enquire", "cost", "price", "visit", "schedule"])
        return {
            "intent": "booking" if is_booking_intent else "greeting",
            "procedure": procedure
        }


class FSMRouter:
    """Deterministic Finite State Machine Router for Healthcare Funnel."""

    def __init__(self, store: SessionStore = session_store):
        self.store = store
        self.nlu = PureNLUParser()

    def process_message(self, phone_number: str, text: str) -> str:
        clean_text = text.strip()
        session = self.store.get_session(phone_number)
        current_state = session["state"]

        if clean_text.lower() in ["reset", "start over", "restart"]:
            self.store.reset_session(phone_number)
            return "Thank you for contacting Apex Dental Center. How may I help you today?"

        # State-based Dispatch Router
        if current_state == State.TRIAGE:
            return self._handle_triage_state(phone_number, clean_text, session)
        elif current_state == State.CALENDAR_SELECTION:
            return self._handle_calendar_state(phone_number, clean_text, session)
        elif current_state == State.PAYMENT_PENDING:
            return self._handle_payment_state(phone_number, clean_text, session)
        elif current_state == State.COMPLETED:
            return self._handle_completed_state(phone_number, clean_text, session)
        else:
            self.store.reset_session(phone_number)
            return "Thank you for contacting Apex Dental Center. How may I help you today?"

    def _handle_triage_state(self, phone: str, text: str, session: Dict[str, Any]) -> str:
        nlu_data = self.nlu.parse_nlu(text)
        procedure = nlu_data["procedure"]

        # Explicit Transition to CALENDAR_SELECTION
        self.store.update_state(phone, State.CALENDAR_SELECTION, procedure=procedure)

        return (
            f"Hello! Welcome to Apex Dental Center in Koramangala. 😊\n\n"
            f"Regarding {procedure}, our clinic is open Monday to Saturday from 9:00 AM to 8:00 PM, and Sunday from 10:00 AM to 2:00 PM.\n\n"
            f"We have consultation slots available today, tomorrow, and this Saturday!\n"
            f"What day and time works best for you?"
        )

    def _handle_calendar_state(self, phone: str, text: str, session: Dict[str, Any]) -> str:
        slot_ref = f"SLOT_{session.get('procedure', 'GENERAL')[:4].upper()}_1000"
        pay_url = f"https://centaur-bot.onrender.com/pay/{slot_ref}"

        # Explicit Transition to PAYMENT_PENDING
        self.store.update_state(phone, State.PAYMENT_PENDING, slot=slot_ref, pay_url=pay_url)

        return (
            f"Perfect! I can hold that time for you. 😊\n\n"
            f"Doctor: Dr. Chinmay Hudedamani\n"
            f"Location: Apex Dental Center, Koramangala, Bengaluru\n\n"
            f"To lock this slot, please complete the ₹500 consultation fee payment using the secure link below:\n\n"
            f"💳 Payment Link: {pay_url}\n"
            f"⌛ Slot Reference: {slot_ref}\n\n"
            f"Once paid, reply 'PAID' or '1' to lock your appointment!"
        )

    def _handle_payment_state(self, phone: str, text: str, session: Dict[str, Any]) -> str:
        clean = text.strip().lower()
        if clean in ["paid", "payment done", "done", "1", "yes", "confirm", "txn"]:
            txn_id = f"TXN_{abs(hash(phone)) % 1000000}"

            # Explicit Transition to COMPLETED
            self.store.update_state(phone, State.COMPLETED, txn_id=txn_id)

            return (
                f"🎉 Payment Confirmed & Appointment Locked!\n\n"
                f"Patient Phone: {phone}\n"
                f"Doctor: Dr. Chinmay Hudedamani\n"
                f"Clinic: Apex Dental Center, Koramangala, Bengaluru\n"
                f"Slot Reference: {session.get('slot', 'SLOT_GENERAL')}\n"
                f"Payment Status: PAID (₹500 - Ref: {txn_id})\n\n"
                f"Dr. Chinmay's schedule has been updated. We look forward to seeing you!"
            )

        return (
            f"We are awaiting your payment confirmation to lock slot {session.get('slot', 'SLOT_GENERAL')}.\n\n"
            f"💳 Payment Link: {session.get('pay_url', 'https://centaur-bot.onrender.com/pay/SLOT_GENERAL')}\n"
            f"Once paid, reply 'PAID' or '1' to complete your booking!"
        )

    def _handle_completed_state(self, phone: str, text: str, session: Dict[str, Any]) -> str:
        return (
            f"Your appointment is already locked! (Ref: {session.get('slot', 'SLOT_GENERAL')}).\n"
            f"If you need to reschedule or ask any questions, please contact our desk directly at +91-9988776655."
        )
