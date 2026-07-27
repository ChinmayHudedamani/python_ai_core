# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Multi-Role Streamlit Demo Application & WhatsApp Simulator

import os
import json
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.core.config import settings
from app.services.schemas import MIDGODentalResponse
from app.services.llm_client import GeminiMIDGOClient

load_dotenv()

# ==========================================
# 1. PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="Apex AI Clinic Demo Suite",
    page_icon="🏥",
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
# 2. SESSION & STATE ENGINE
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
        "content": (
            "Hey there! 👋 I'm APEX AI, your clinical assistant from Apex Dental Center & Implant Institute, Koramangala. 🌿\n\n"
            "I'm here to guide you, answer your health questions, and connect you to care when needed.\n\n"
            "To start, may I know your primary symptom or health concern today?"
        )
    }]

# ==========================================
# 3. SIDEBAR: ROLE SWITCHER & STATE INSPECTOR
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/dental-braces.png", width=64)
    st.title("Apex AI Hub")
    st.caption("Multi-Role Demo & State Inspector")
    st.markdown("---")
    
    role = st.selectbox(
        "Select User Persona / View",
        ["Patient WhatsApp View", "Doctor Command Center", "Receptionist Operations Dashboard"]
    )
    
    st.markdown("---")
    st.subheader("🔍 Live State Memory")
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
# 4. VIEW ROUTER
# ==========================================
if role == "Patient WhatsApp View":
    st.title("💬 Apex Dental — WhatsApp AI Assistant")
    st.caption("Powered by Gemini 2.5 Flash & TrueLark MIDGO Architecture")

    # Render chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])

    # User Input Handler
    if user_input := st.chat_input("Type your WhatsApp message here..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

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

        try:
            ai_client = GeminiMIDGOClient()
            result: MIDGODentalResponse = ai_client.process_turn(system_prompt, user_input)

            if result.extracted_name:
                current_state["name"] = result.extracted_name
            if result.extracted_symptom_or_reason:
                current_state["symptom"] = result.extracted_symptom_or_reason

            reply_text = result.patient_reply

            if current_state["name"] and current_state["symptom"] and not current_state["slot_confirmed"]:
                if "10:30" in user_input or "2:00" in user_input or "4:30" in user_input:
                    current_state["slot_confirmed"] = True
                    current_state["confirmed_slot"] = user_input
                    reply_text = f"✅ Fantastic! Your appointment is locked in for {user_input} with Dr. Chinmay Hudedamani. Check-in code is APX-4928. We'll see you at Koramangala!"
                else:
                    reply_text += " We have available consultation slots tomorrow with Dr. Chinmay Hudedamani: • 10:30 AM • 02:00 PM • 04:30 PM. Which works best?"

            st.session_state.session_db = current_state

            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(reply_text)
            
            st.session_state.messages.append({"role": "assistant", "content": reply_text})

        except Exception as e:
            error_msg = f"⚠️ System notice: Encountered an exception while processing your request ({e}). Please ensure your `GEMINI_API_KEY` is configured correctly in `.env`."
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

elif role == "Doctor Command Center":
    st.title("👨‍⚕️ Doctor Command Center")
    st.caption("Dr. Chinmay Hudedamani — Executive Operations")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Today's Appointments", "12 Patients")
    col2.metric("Confirmed Check-Ins", "8 Patients")
    col3.metric("Emergency Triages", "1 Patient")

    st.markdown("---")
    st.subheader("📋 Active Patient Roster")
    st.dataframe([
        {"Time": "10:30 AM", "Patient": "Rahul Sharma", "Symptom": "Lower Molar Toothache", "Status": "CONFIRMED", "Code": "APX-4928"},
        {"Time": "11:15 AM", "Patient": "Priya Nair", "Symptom": "Teeth Whitening Consult", "Status": "CHECKED_IN", "Code": "APX-8237"},
        {"Time": "02:00 PM", "Patient": "Ananya Roy", "Symptom": "Crown Replacement", "Status": "SLOT_HELD", "Code": "APX-3912"},
    ], use_container_width=True)

else:
    st.title("👩‍💼 Receptionist Dashboard")
    st.caption("Apex Dental Koramangala — Front Desk Operations")
    
    st.subheader("⚡ Quick Patient Check-In Verifier")
    checkin_code = st.text_input("Enter 6-Character Check-In Code (e.g., APX-4928)")
    if st.button("Verify & Check-In Patient"):
        if checkin_code.upper() == "APX-4928":
            st.success("✅ Code APX-4928 Verified! Patient: Rahul Sharma | Slot: 10:30 AM | Dr. Chinmay Hudedamani")
        else:
            st.warning(f"Searching database for code '{checkin_code}'...")
