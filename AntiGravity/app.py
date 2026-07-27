# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX Dental Center AI Concierge — Yelahanka Node v0.2 (TrueLark MIDGO Architecture)

import os
import json
import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# ==========================================
# 1. PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="Apex Dental Yelahanka — AI Concierge v0.2",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stChatFloatingInputContainer {bottom: 20px;}
    .quick-btn-container {margin-bottom: 15px;}
    .metric-card {background-color: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #e9ecef;}
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
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.model = os.getenv("DEFAULT_LLM_MODEL", "gemini-2.5-flash")

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
# 4. SESSION & STATE ENGINE
# ==========================================
if "session_db" not in st.session_state:
    st.session_state.session_db = {
        "name": "",
        "symptom": "",
        "node_location": "Yelahanka Node v0.2",
        "slot_confirmed": False,
        "confirmed_slot": None
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
# 5. SIDEBAR: LIVE TELEMETRY & STATE INSPECTOR
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/dental-braces.png", width=64)
    st.title("Apex AI Ops Hub")
    st.caption("Yelahanka Node v0.2 | TrueLark MIDGO Architecture")
    st.markdown("---")
    st.subheader("🔍 Live MIDGO State DB")
    
    # Real-time inspection of backend memory
    st.json(st.session_state.session_db)
    
    st.markdown("---")
    st.subheader("🏥 Node Profile")
    st.write("• **Branch**: Yelahanka 5th Phase")
    st.write("• **Landmark**: Major Sandeep Unnikrishnan Rd")
    st.write("• **Valet Parking**: Available (Free Basement)")
    st.write("• **Head Surgeon**: Dr. Chinmay Hudedamani")

    st.markdown("---")
    if st.button("🔄 Reset Patient Session"):
        st.session_state.session_db = {
            "name": "",
            "symptom": "",
            "node_location": "Yelahanka Node v0.2",
            "slot_confirmed": False,
            "confirmed_slot": None
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
st.caption("Powered by Gemini 2.5 Flash & TrueLark MIDGO Framework")

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
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    # Build system prompt with current state injection & Yelahanka Node Rules
    current_state = st.session_state.session_db
    system_prompt = f"""
    You are 'Apex Assistant', the highly empathetic AI receptionist at Apex Dental Center & Implant Institute, Yelahanka Node v0.2. 
    Your ultimate goal is to triage the symptom, gather the patient's name, and book an appointment slot. 
    Never give up on this goal, but never sound mechanical or pushy.

    CURRENT SYSTEM KNOWLEDGE OF THIS PATIENT:
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

    # Process through Gemini MIDGO Client
    try:
        ai_client = GeminiMIDGOClient()
        result: MIDGODentalResponse = ai_client.process_turn(system_prompt, user_input)

        # Silent Backend State Synchronization
        if result.extracted_name:
            current_state["name"] = result.extracted_name
        if result.extracted_symptom_or_reason:
            current_state["symptom"] = result.extracted_symptom_or_reason

        reply_text = result.patient_reply

        # Handle slot selection flow if core data is present
        if current_state["name"] and current_state["symptom"] and not current_state["slot_confirmed"]:
            if "10:30" in user_input or "2:00" in user_input or "4:30" in user_input or "yes" in user_input.lower():
                current_state["slot_confirmed"] = True
                current_state["confirmed_slot"] = user_input
                reply_text = f"✅ Fantastic! Your appointment is locked in for {user_input} with Dr. Chinmay Hudedamani. Check-in code is APX-4928. We'll see you at Yelahanka Node!"
            else:
                reply_text += " We have available consultation slots tomorrow at Yelahanka with Dr. Chinmay Hudedamani: • 10:30 AM • 02:00 PM • 04:30 PM. Which works best?"

        st.session_state.session_db = current_state

        # Display Assistant Response
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(reply_text)
        
        st.session_state.messages.append({"role": "assistant", "content": reply_text})

    except Exception as e:
        error_msg = f"⚠️ System notice: Encountered an exception while processing your request. Please ensure your `GEMINI_API_KEY` is configured correctly in `.env`."
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(error_msg)
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
