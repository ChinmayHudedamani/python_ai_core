# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX Dental Center AI Concierge — Yelahanka Node v0.2
# Architecture: TrueLark MIDGO + Deterministic FSG Bounded Branching (M1 - M5 Macro-States)

import os
import json
import random
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from app.core.config import settings

# Load Environment Variables
load_dotenv()

# ==========================================
# 1. PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="Apex Dental Yelahanka Node v0.2 — AI Concierge",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stChatFloatingInputContainer {bottom: 20px;}
    .metric-card {background-color: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #e9ecef;}
    .state-badge {background-color: #e3f2fd; color: #0d47a1; padding: 4px 8px; border-radius: 4px; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SCHEMAS: MIDGO Dual-Output Structure
# ==========================================
class MIDGODentalResponse(BaseModel):
    extracted_name: str = Field(
        default="",
        description="Patient's full name if mentioned in this turn or previous context, otherwise empty string."
    )
    extracted_symptom_or_reason: str = Field(
        default="",
        description="Core symptom, reason for visit, or emergency status if mentioned, otherwise empty string."
    )
    classified_intent: str = Field(
        default="BOOKING_SLOT",
        description="Intent tag: BOOKING_SLOT, FAQ_INQUIRY, EMERGENCY_TRIAGE, or STATUS_LOOKUP."
    )
    patient_reply: str = Field(
        ...,
        description=(
            "Dynamic, empathetic message back to the patient. "
            "MIDGO Rule: If the patient brought up a tangent or FAQ (e.g., parking, pricing, insurance, tablets, location), "
            "address it warmly and reassuringly in the first sentence, then smoothly pivot back to collecting the next missing goal field."
        )
    )

# ==========================================
# 3. LLM CLIENT: Gemini Structured Output Handler
# ==========================================
class GeminiMIDGOClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", None)
        self.client = genai.Client(api_key=api_key)
        self.model = os.getenv("DEFAULT_LLM_MODEL") or getattr(settings, "DEFAULT_LLM_MODEL", "gemini-2.5-flash")

    def process_turn(self, system_prompt: str, user_message: str) -> MIDGODentalResponse:
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_schema=MIDGODentalResponse,
                    temperature=0.3,
                ),
            )
            return MIDGODentalResponse.model_validate_json(response.text)
        except Exception as e:
            return MIDGODentalResponse(
                extracted_name="",
                extracted_symptom_or_reason="",
                classified_intent="FAQ_INQUIRY",
                patient_reply="I understand! Let me connect you to our Yelahanka Node front desk team who can assist you right away!"
            )

# ==========================================
# 4. DETERMINISTIC FINITE STATE GRAPH (FSG) M1 - M5
# ==========================================
MACRO_STATES = {
    "M1_INTAKE": "M1: Patient Intake & Symptom Triage",
    "M2_FAQ_DETOUR": "M2: Tangent / FAQ Inquiry Resolution",
    "M3_IDENTIFICATION": "M3: Patient Name Collection",
    "M4_SLOT_SELECTION": "M4: Slot Selection & Availability",
    "M5_BOOKING_CONFIRMED": "M5: Appointment Locked (APX Code Generated)"
}

def update_macro_state(db: dict) -> str:
    """Computes the current Finite State Graph (FSG) Macro-State."""
    if db["slot_confirmed"]:
        return "M5_BOOKING_CONFIRMED"
    elif db["name"] and db["symptom"]:
        return "M4_SLOT_SELECTION"
    elif db["symptom"] and not db["name"]:
        return "M3_IDENTIFICATION"
    else:
        return "M1_INTAKE"

# Initialize Session Memory
if "session_db" not in st.session_state:
    st.session_state.session_db = {
        "macro_state": "M1_INTAKE",
        "name": "",
        "symptom": "",
        "node_location": "Yelahanka Node v0.2",
        "slot_confirmed": False,
        "confirmed_slot": None,
        "check_in_code": None
    }

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": (
            "Hey there! 👋 I'm APEX AI, your clinical assistant from Apex Dental Center & Implant Institute, Yelahanka Node v0.2. 🌿\n\n"
            "I'm here to guide you, answer your health questions, and connect you to care when needed.\n\n"
            "To start, may I know your primary symptom or health concern today?"
        )
    }]

# ==========================================
# 5. SIDEBAR: LIVE TELEMETRY & FSG STATE INSPECTOR
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/dental-braces.png", width=64)
    st.title("Apex AI Ops Hub")
    st.caption("Yelahanka Node v0.2 | TrueLark MIDGO Architecture")
    st.markdown("---")
    
    # Current Macro-State Badge
    current_macro = update_macro_state(st.session_state.session_db)
    st.session_state.session_db["macro_state"] = current_macro
    st.markdown(f"**Active FSG State:** <span class='state-badge'>{current_macro}</span>", unsafe_allow_html=True)
    st.caption(MACRO_STATES[current_macro])
    
    st.markdown("---")
    st.subheader("🔍 Live MIDGO Memory DB")
    st.json(st.session_state.session_db)
    
    st.markdown("---")
    st.subheader("🏥 Node Profile")
    st.write("• **Branch**: Yelahanka 5th Phase")
    st.write("• **Landmark**: Major Sandeep Unnikrishnan Rd")
    st.write("• **Valet Parking**: Available (Free Basement)")
    st.write("• **Head Surgeon**: Dr. Chinmay Hudedamani (MDS)")
    st.write("• **Hours**: Mon-Sat 09:00 AM - 08:30 PM | Sun 10:00 AM - 02:00 PM")

    st.markdown("---")
    if st.button("🔄 Reset Patient Session"):
        st.session_state.session_db = {
            "macro_state": "M1_INTAKE",
            "name": "",
            "symptom": "",
            "node_location": "Yelahanka Node v0.2",
            "slot_confirmed": False,
            "confirmed_slot": None,
            "check_in_code": None
        }
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Session reset. How can I help you with your dental care at Yelahanka Node today?"
        }]
        st.rerun()

# ==========================================
# 6. MAIN CHAT INTERFACE & MIDGO EXECUTION
# ==========================================
st.title("🦷 Apex Dental Center — Yelahanka Node v0.2")
st.caption("Powered by Gemini 2.5 Flash & TrueLark MIDGO FSG Engine")

# Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])

# Quick-Action FAQ Buttons Above Chat Input
st.markdown("##### ⚡ Quick FAQ Curveball Inputs:")
faq_cols = st.columns(5)
selected_faq = None

with faq_cols[0]:
    if st.button("🚗 Valet Parking?"):
        selected_faq = "Do you have free valet parking at Yelahanka?"
with faq_cols[1]:
    if st.button("💊 Painkiller Request?"):
        selected_faq = "Can you prescribe painkiller tablets for my toothache?"
with faq_cols[2]:
    if st.button("💰 Root Canal Cost?"):
        selected_faq = "How much does a microscopic root canal cost?"
with faq_cols[3]:
    if st.button("📍 Clinic Location?"):
        selected_faq = "Where exactly is the Yelahanka Node located?"
with faq_cols[4]:
    if st.button("🦷 TMJ Jaw Click?"):
        selected_faq = "My jaw makes a clicking sound when I chew."

# User Input Handler
chat_text = st.chat_input("Type your message here...")
user_input = selected_faq or chat_text

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    current_state = st.session_state.session_db
    
    # Build System Instruction with Active FSG Macro-State Injection
    system_prompt = f"""
    You are 'Apex Assistant', the highly empathetic AI receptionist at Apex Dental Center & Implant Institute, Yelahanka Node v0.2. 
    Your ultimate goal is to triage the symptom, gather the patient's name, and book an appointment slot. 
    Never give up on this goal, but never sound mechanical or pushy.

    CURRENT FINITE STATE GRAPH (FSG) MACRO-STATE: {current_state['macro_state']}
    CURRENT PATIENT MEMORY:
    - Name: "{current_state['name'] or 'Unknown'}"
    - Symptom/Reason: "{current_state['symptom'] or 'Unknown'}"
    - Slot Confirmed: {current_state['slot_confirmed']}

    YELAHANKA NODE v0.2 OFFICE RULES & FAQ:
    - Location: 5th Phase, Yelahanka New Town, Bengaluru (near Major Sandeep Unnikrishnan Road). Free basement valet parking available!
    - Operating Hours: Mon-Sat: 09:00 AM - 08:30 PM | Sun: 10:00 AM - 02:00 PM.
    - Insurance: We accept all major insurances (HDFC ERGO, Star Health, ICICI Lombard, Max Bupa).
    - Doctor: Dr. Chinmay Hudedamani (MDS, Oral & Maxillofacial Surgeon & Implantologist).
    - Pricing: Root Canal (₹4,500 - ₹7,500), Dental Implants (₹25,000 - ₹45,000), General Consult (₹700).

    CONVERSATION STYLE INSTRUCTIONS (Mixed-Initiative MIDGO Framework):
    1. Actively listen. If the patient asks about parking, location, pricing, insurance, or medications/tablets, address it natively and reassuringly in the first sentence of your reply.
    2. Immediately after answering their question, smoothly pivot back to collecting the missing information needed to book them.
    3. Never use generic template phrases. Speak naturally like a human receptionist.
    4. Keep your `patient_reply` concise (under 3 sentences) so it reads well.
    """

    try:
        ai_client = GeminiMIDGOClient()
        result: MIDGODentalResponse = ai_client.process_turn(system_prompt, user_input)

        # Silent Backend State Extraction & Synchronization
        if result.extracted_name and result.extracted_name.lower() not in ["unknown", "none"]:
            current_state["name"] = result.extracted_name
        if result.extracted_symptom_or_reason and result.extracted_symptom_or_reason.lower() not in ["unknown", "none"]:
            current_state["symptom"] = result.extracted_symptom_or_reason

        reply_text = result.patient_reply

        # Handle FSG State Transitions for Slot Selection & Lock
        if current_state["name"] and current_state["symptom"] and not current_state["slot_confirmed"]:
            if any(t in user_input.lower() for t in ["10:30", "2:00", "4:30", "yes", "sure", "confirm", "10", "2", "4"]):
                code_num = random.randint(1000, 9999)
                check_in_code = f"APX-{code_num}"
                current_state["slot_confirmed"] = True
                current_state["confirmed_slot"] = user_input
                current_state["check_in_code"] = check_in_code
                reply_text = (
                    f"✅ Fantastic, {current_state['name']}! Your appointment is locked in for {user_input} "
                    f"with Dr. Chinmay Hudedamani at Yelahanka Node v0.2. "
                    f"Your check-in code is **{check_in_code}**. We look forward to seeing you!"
                )
            else:
                reply_text += (
                    f" We have open consultation slots tomorrow at Yelahanka Node for {current_state['name']}: "
                    "• 10:30 AM • 02:00 PM • 04:30 PM. Which time works best for you?"
                )

        # Update Final FSG State after processing
        current_state["macro_state"] = update_macro_state(current_state)
        st.session_state.session_db = current_state

        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(reply_text)
        
        st.session_state.messages.append({"role": "assistant", "content": reply_text})

    except Exception as e:
        error_msg = f"⚠️ System notice: Encountered an exception while processing your request ({e}). Please ensure your `GEMINI_API_KEY` is configured correctly in `.env`."
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(error_msg)
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
