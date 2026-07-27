import os
import json
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from app.core.config import settings

load_dotenv()

# ==========================================
# 1. PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="Apex AI Clinic Concierge",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stChatFloatingInputContainer {bottom: 20px;}
    .metric-card {background-color: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #e9ecef;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SCHEMAS: MIDGO Dual-Output Structure
# ==========================================
class MIDGODentalResponse(BaseModel):
    extracted_name: str = Field(description="Patient's full name if mentioned in this turn or previous context, otherwise empty string.")
    extracted_symptom_or_reason: str = Field(description="Core symptom, reason for visit, or emergency status if mentioned, otherwise empty string.")
    classified_intent: str = Field(description="Intent tag: BOOKING_SLOT, FAQ_INQUIRY, EMERGENCY_TRIAGE, or STATUS_LOOKUP.")
    
    patient_reply: str = Field(
        description="Dynamic, empathetic message back to the patient. "
                    "MIDGO Rule: If the patient brought up a tangent or FAQ (e.g., parking, pricing, insurance, tablets, location), "
                    "address it warmly and reassuringly in the first sentence, then smoothly pivot back to collecting the next missing goal field."
    )

# ==========================================
# 3. LLM CLIENT: Gemini Structured Output Handler
# ==========================================
class GeminiMIDGOClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY") or settings.GEMINI_API_KEY
        self.client = genai.Client(api_key=api_key)
        self.model = os.getenv("DEFAULT_LLM_MODEL") or settings.DEFAULT_LLM_MODEL or "gemini-2.5-flash"

    def process_turn(self, system_prompt: str, user_message: str) -> MIDGODentalResponse:
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

# ==========================================
# 4. SESSION & STATE ENGINE
# ==========================================
if "session_db" not in st.session_state:
    st.session_state.session_db = {
        "name": "",
        "symptom": "",
        "slot_confirmed": False,
        "confirmed_slot": None
    }

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hey there! 👋 I'm APEX AI, your clinical assistant from Apex Dental Center & Implant Institute, Koramangala. 🌿\nI'm here to guide you, answer your health questions, and connect you to care when needed.\nTo start, may I know your primary symptom or health concern today?"
    }]

# ==========================================
# 5. SIDEBAR: LIVE STATE INSPECTOR (MIDGO)
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/dental-braces.png", width=64)
    st.title("Apex AI Ops Hub")
    st.markdown("---")
    st.subheader("🔍 Live MIDGO State DB")
    
    # Real-time inspection of backend memory
    st.json(st.session_state.session_db)
    
    st.markdown("---")
    if st.button("🔄 Reset Patient Session"):
        st.session_state.session_db = {"name": "", "symptom": "", "slot_confirmed": False, "confirmed_slot": None}
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Session reset. How can I help you with your dental care today?"
        }]
        st.rerun()

# ==========================================
# 6. MAIN CHAT INTERFACE & MIDGO EXECUTION
# ==========================================
st.title("🦷 Apex Dental Center - Live AI Concierge")
st.caption("Powered by Gemini 2.5 Flash & TrueLark MIDGO Architecture")

# Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])

# User Input Handler
if user_input := st.chat_input("Type your message here..."):
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    # Build system prompt with current state injection
    current_state = st.session_state.session_db
    system_prompt = f"""
    You are 'Apex Assistant', the highly empathetic AI receptionist at Apex Dental Center & Implant Institute, Koramangala. 
    Your ultimate goal is to triage the symptom, gather the patient's name, and book an appointment slot. 
    Never give up on this goal, but never sound mechanical or pushy.

    CURRENT SYSTEM KNOWLEDGE OF THIS PATIENT:
    - Name: "{current_state['name'] or 'Unknown'}"
    - Symptom/Reason: "{current_state['symptom'] or 'Unknown'}"
    - Slot Confirmed: {current_state['slot_confirmed']}

    DENTAL OFFICE RULES & FAQ:
    - Location: 104, 80 Feet Road, 4th Block, Koramangala (near Sony World Signal). Free basement valet parking available!
    - Insurance: We accept all major insurances.
    - Doctor: Dr. Chinmay Hudedamani.

    CONVERSATION STYLE INSTRUCTIONS (Mixed-Initiative MIDGO Framework):
    1. Actively listen. If the patient asks about parking, location, pricing, or medications/tablets, address it natively and reassuringly in the first sentence of your reply.
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
            if "10:30" in user_input or "2:00" in user_input or "4:30" in user_input:
                current_state["slot_confirmed"] = True
                current_state["confirmed_slot"] = user_input
                reply_text = f"✅ Fantastic! Your appointment is locked in for {user_input} with Dr. Chinmay Hudedamani. Check-in code is APX-4928. We'll see you at Koramangala!"
            else:
                reply_text += " We have available consultation slots tomorrow with Dr. Chinmay Hudedamani: • 10:30 AM • 02:00 PM • 04:30 PM. Which works best?"

        st.session_state.session_db = current_state

        # Display Assistant Response
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(reply_text)
        
        st.session_state.messages.append({"role": "assistant", "content": reply_text})

    except Exception as e:
        error_msg = f"⚠️ System notice: Encountered an exception while processing your request ({e}). Please ensure your `GEMINI_API_KEY` is configured correctly in `.env`."
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(error_msg)
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
