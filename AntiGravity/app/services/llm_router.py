# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Phone-Based Role-Based Access Control (RBAC) Router & Dual-Agent System Prompts

import os
import logging
import phonenumbers
from typing import Dict, Any, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.tools import PatientToolsRegistry
from app.services.admin_tools import AdminToolsRegistry
from app.services.llm_client import GeminiClientWrapper

logger = logging.getLogger("APEX_AI_RBAC_ROUTER")

# Load authorized doctor phone numbers from environment
RAW_DOCTOR_PHONES = os.getenv("AUTHORIZED_DOCTOR_PHONES", "+917338350871,7338350871")

DOCTOR_SYSTEM_PROMPT = """You are the AI Executive Assistant to Dr. Chinmay Hudedamani, Head Surgeon at Apex Dental Center.
Your sole role is to provide the doctor with clear, concise, and instant operational data regarding clinic ledgers, daily appointment schedules, patient symptoms, and financial revenue projections.
DO NOT act like a patient receptionist. Do not ask for symptoms or offer treatment advice. Speak professionally and concisely.
"""

PATIENT_SYSTEM_PROMPT = """You are APEX AI, the WhatsApp clinical assistant for Apex Dental Center & Implant Institute, Koramangala, Bengaluru.
You are not a dentist and never claim clinical authority. Your job is threefold:
1. Safety — never give medical advice, diagnoses, or medication guidance.
2. Grounding — never state a fact that isn't in the clinical data provided to you.
3. Conversion — guide the patient toward a booked, confirmed consultation slot with minimum friction.
CRITICAL SYMPTOM RULE: Before reserving a slot with create_booking, you MUST ask the patient for their primary symptom or health concern.
PRAGMATIC SHORT-TEXT RULE: The user may frequently reply with shorthand, single words, or conversational confirmations (e.g., 'Yes', 'Tomorrow', 'Price?'). Always resolve these micro-inputs using the immediate conversation history and active session context. Never ask generic clarification questions if the context makes the intent obvious.
"""


def _normalize_phone(phone: str) -> str:
    """Normalizes phone number to E164 string format."""
    try:
        parsed = phonenumbers.parse(phone, "IN")
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except Exception:
        pass
    clean = phone.replace("+", "").replace("-", "").replace(" ", "").strip()
    return f"+91{clean}" if len(clean) == 10 else f"+{clean}"


def is_authorized_doctor(phone_number: str) -> bool:
    """Checks if inbound phone number matches an authorized doctor phone."""
    clean_inbound = _normalize_phone(phone_number)
    authorized_list = [p.strip() for p in RAW_DOCTOR_PHONES.split(",") if p.strip()]

    for doc_phone in authorized_list:
        if _normalize_phone(doc_phone) == clean_inbound or doc_phone in clean_inbound:
            return True
    return False


def get_agent_context(inbound_phone: str) -> Tuple[str, Any, str]:
    """RBAC Dispatcher: Returns system prompt, bound tool registry, and agent role name."""
    if is_authorized_doctor(inbound_phone):
        logger.info(f"👨‍⚕️ RBAC Authorized: Loaded Doctor Executive Assistant persona for {inbound_phone}")
        return DOCTOR_SYSTEM_PROMPT, AdminToolsRegistry, "DOCTOR_EXECUTIVE_ASSISTANT"
    else:
        logger.info(f"👤 RBAC Public: Loaded Patient Concierge persona for {inbound_phone}")
        return PATIENT_SYSTEM_PROMPT, PatientToolsRegistry, "PATIENT_CONCIERGE"


async def dispatch_tool_execution(
    inbound_phone: str,
    tool_name: str,
    db: AsyncSession,
    kwargs: Dict[str, Any]
) -> Dict[str, Any]:
    """Executes tool ONLY if the agent persona is authorized for that tool registry."""
    _, bound_registry, role = get_agent_context(inbound_phone)

    if role == "PATIENT_CONCIERGE" and tool_name in ["get_daily_ledger", "get_revenue_report", "reschedule_or_cancel_appointment"]:
        logger.warning(f"🚨 RBAC ACCESS DENIED: Public patient {inbound_phone} attempted to execute admin tool '{tool_name}'!")
        return {
            "success": False,
            "error": f"Access Denied: Tool '{tool_name}' requires doctor administrative authorization."
        }

    return await bound_registry.execute(name=tool_name, db=db, kwargs=kwargs)


async def process_user_message_with_gemini(
    inbound_phone: str,
    user_message: str,
    db: Optional[AsyncSession] = None
) -> Dict[str, Any]:
    """Routes message to bound system persona and invokes Gemini 2.5 Flash SDK generation."""
    system_prompt, _, role = get_agent_context(inbound_phone)
    client = GeminiClientWrapper()

    reply_text = await client.generate_response(
        system_prompt=system_prompt,
        user_message=user_message
    )

    return {
        "role": role,
        "phone": inbound_phone,
        "response": reply_text,
        "model": client.model
    }
