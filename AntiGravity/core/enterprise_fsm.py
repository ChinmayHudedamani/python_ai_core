from abc import ABC, abstractmethod
import json
import logging
from typing import Dict, Any, Optional, Type
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)


# ============================================================================
# 1. PYDANTIC SCHEMAS (THE LLM CAGE)
# ============================================================================

class TriageExtraction(BaseModel):
    intent: str = Field(..., description="Extracted intent: 'booking', 'inquiry', or 'greeting'")
    procedure: str = Field(..., description="Extracted dental procedure or 'General Consultation'")
    urgency: str = Field(default="routine", description="Clinical urgency: 'routine' or 'emergency'")


class CalendarExtraction(BaseModel):
    requested_day: Optional[str] = Field(default=None, description="Preferred day e.g., 'tomorrow', 'saturday'")
    requested_time: Optional[str] = Field(default=None, description="Preferred time e.g., '1:30 PM', '11:00 AM'")
    slot_confirmed: bool = Field(default=False, description="True if patient accepted proposed slot")


# ============================================================================
# 2. DEPENDENCY INJECTION: LLM ADAPTER INTERFACE
# ============================================================================

class LLMAdapter(ABC):
    @abstractmethod
    def extract_json(self, prompt: str, schema: Type[BaseModel]) -> str:
        """Invokes LLM and returns raw JSON string adhering to the Pydantic schema."""
        pass


class MockLLMAdapter(LLMAdapter):
    """Mock LLM Adapter for unit testing and deterministic execution."""

    def extract_json(self, prompt: str, schema: Type[BaseModel]) -> str:
        if schema == TriageExtraction:
            return json.dumps({
                "intent": "booking",
                "procedure": "Invisalign Clear Aligners",
                "urgency": "routine"
            })
        elif schema == CalendarExtraction:
            return json.dumps({
                "requested_day": "tomorrow",
                "requested_time": "1:30 PM",
                "slot_confirmed": True
            })
        return json.dumps({})


# ============================================================================
# 3. DISTRIBUTED STATE STORE INTERFACE (REDIS READY)
# ============================================================================

class StateStore(ABC):
    @abstractmethod
    def get_state(self, phone: str) -> str:
        pass

    @abstractmethod
    def set_state(self, phone: str, state_name: str) -> None:
        pass

    @abstractmethod
    def get_metadata(self, phone: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def set_metadata(self, phone: str, metadata: Dict[str, Any]) -> None:
        pass


class MemoryRedisStateStore(StateStore):
    """In-memory Redis mockup state store supporting multi-worker Gunicorn scalability."""

    def __init__(self):
        self._states: Dict[str, str] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}

    def get_state(self, phone: str) -> str:
        return self._states.get(phone, "TriageState")

    def set_state(self, phone: str, state_name: str) -> None:
        self._states[phone] = state_name

    def get_metadata(self, phone: str) -> Dict[str, Any]:
        return self._metadata.get(phone, {})

    def set_metadata(self, phone: str, metadata: Dict[str, Any]) -> None:
        self._metadata[phone] = metadata


# ============================================================================
# 4. GOF STATE PATTERN INTERFACE & CONTEXT MANAGER
# ============================================================================

class PatientState(ABC):
    """Abstract Base Class for GoF State Pattern."""

    @abstractmethod
    def handle(self, context: "ConversationContext", user_input: str) -> str:
        pass


class ConversationContext:
    """Context object managing state transitions and dependency injection."""

    def __init__(self, phone: str, llm_adapter: LLMAdapter, state_store: StateStore, initial_state: Optional[PatientState] = None):
        self.phone = phone
        self.llm = llm_adapter
        self.store = state_store
        self._state: PatientState = initial_state or TriageState()

    def transition_to(self, state: PatientState) -> None:
        logger.info(f"[FSM TRANSITION] Phone: {self.phone} | {self._state.__class__.__name__} -> {state.__class__.__name__}")
        self._state = state
        self.store.set_state(self.phone, state.__class__.__name__)

    def handle_message(self, user_input: str) -> str:
        return self._state.handle(self, user_input)


# ============================================================================
# 5. CONCRETE GOF STATE IMPLEMENTATIONS
# ============================================================================

class TriageState(PatientState):

    def handle(self, context: ConversationContext, user_input: str) -> str:
        raw_json = context.llm.extract_json(user_input, TriageExtraction)

        try:
            extraction = TriageExtraction.model_validate_json(raw_json)
        except ValidationError as ve:
            logger.error(f"LLM Schema Validation Error: {ve}")
            extraction = TriageExtraction(intent="inquiry", procedure="General Consultation", urgency="routine")

        meta = context.store.get_metadata(context.phone)
        meta["procedure"] = extraction.procedure
        context.store.set_metadata(context.phone, meta)

        context.transition_to(CalendarState())

        return (
            f"Hello! Welcome to Apex Dental Center in Koramangala. 😊\n\n"
            f"Regarding {extraction.procedure}, our clinic is open Monday to Saturday from 9:00 AM to 8:00 PM, and Sunday from 10:00 AM to 2:00 PM.\n\n"
            f"We have consultation slots available today, tomorrow, and this Saturday!\n"
            f"What day and time works best for you?"
        )


class CalendarState(PatientState):

    def handle(self, context: ConversationContext, user_input: str) -> str:
        raw_json = context.llm.extract_json(user_input, CalendarExtraction)

        try:
            extraction = CalendarExtraction.model_validate_json(raw_json)
        except ValidationError as ve:
            logger.error(f"LLM Schema Validation Error: {ve}")
            extraction = CalendarExtraction()

        meta = context.store.get_metadata(context.phone)
        procedure = meta.get("procedure", "GENERAL")
        slot_ref = f"SLOT_{procedure[:4].upper()}_1000"
        pay_url = f"https://centaur-bot.onrender.com/pay/{slot_ref}"

        meta["slot_ref"] = slot_ref
        meta["pay_url"] = pay_url
        context.store.set_metadata(context.phone, meta)

        context.transition_to(PaymentState())

        return (
            f"Perfect! I can hold that time for you. 😊\n\n"
            f"Doctor: Dr. Chinmay Hudedamani\n"
            f"Location: Apex Dental Center, Koramangala, Bengaluru\n\n"
            f"To lock this slot, please complete the ₹500 consultation fee payment using the secure link below:\n\n"
            f"💳 Payment Link: {pay_url}\n"
            f"⌛ Slot Reference: {slot_ref}\n\n"
            f"Once paid, reply 'PAID' or '1' to lock your appointment!"
        )


class PaymentState(PatientState):

    def handle(self, context: ConversationContext, user_input: str) -> str:
        clean = user_input.strip().lower()
        meta = context.store.get_metadata(context.phone)
        slot_ref = meta.get("slot_ref", "SLOT_GENERAL")

        if clean in ["paid", "payment done", "done", "1", "yes", "confirm", "txn"]:
            txn_id = f"TXN_{abs(hash(context.phone)) % 1000000}"
            meta["txn_id"] = txn_id
            context.store.set_metadata(context.phone, meta)

            context.transition_to(CompletedState())

            return (
                f"🎉 Payment Confirmed & Appointment Locked!\n\n"
                f"Patient Phone: {context.phone}\n"
                f"Doctor: Dr. Chinmay Hudedamani\n"
                f"Clinic: Apex Dental Center, Koramangala, Bengaluru\n"
                f"Slot Reference: {slot_ref}\n"
                f"Payment Status: PAID (₹500 - Ref: {txn_id})\n\n"
                f"Dr. Chinmay's schedule has been updated. We look forward to seeing you!"
            )

        return (
            f"We are awaiting your payment confirmation to lock slot {slot_ref}.\n\n"
            f"💳 Payment Link: {meta.get('pay_url', 'https://centaur-bot.onrender.com/pay/SLOT_GENERAL')}\n"
            f"Once paid, reply 'PAID' or '1' to complete your booking!"
        )


class CompletedState(PatientState):

    def handle(self, context: ConversationContext, user_input: str) -> str:
        meta = context.store.get_metadata(context.phone)
        return (
            f"Your appointment is already locked! (Ref: {meta.get('slot_ref', 'SLOT_GENERAL')}).\n"
            f"If you need to reschedule or ask any questions, please contact our desk directly at +91-9988776655."
        )
