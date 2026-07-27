# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Streamlit Multi-Role Hub — Yelahanka Node v0.2 & Koramangala Demo

import os
import json
import random
import streamlit as st
from pathlib import Path
import sys

# Ensure workspace root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.services.schemas import MIDGODentalResponse, TAXONOMY_30_INTENTS
from app.services.llm_client import GeminiMIDGOClient, log_telemetry_event
from app.services.admin_tools import reschedule_or_cancel_appointment, RescheduleCancelInput

# ==========================================
# 1. PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="Apex AI Clinic Suite — Multi-Role Concierge",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stChatFloatingInputContainer {bottom: 20px;}
    .metric-card {background-color: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #e9ecef;}
    .state-badge {background-color: #e3f2fd; color: #0d47a1; padding: 4px 8px; border-radius: 4px; font-weight: bold;}
    .intent-badge {background-color: #e8f5e9; color: #1b5e20; padding: 3px 6px; border-radius: 4px; font-size: 0.85em;}
    .emergency-badge {background-color: #ffebee; color: #c62828; padding: 4px 8px; border-radius: 4px; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SESSION & STATE ENGINE
# ==========================================
if "session_db" not in st.session_state:
    st.session_state.session_db = {
        "node_id": "Yelahanka_Node_v0.2",
        "macro_state": "M1_STATE_LOGISTICS",
        "last_intent": "INTENT_CLINIC_TIMINGS",
        "name": "",
        "symptom": "",
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

if "doctor_messages" not in st.session_state:
    st.session_state.doctor_messages = [{
        "role": "assistant",
        "content": "Good morning, Dr. Chinmay! 👨‍⚕️ I'm your Executive AI Assistant. You have 12 appointments scheduled today at Yelahanka Node. How can I assist you with your schedule or patient roster?"
    }]

# ==========================================
# 3. SIDEBAR: ROLE SWITCHER & TELEMETRY INSPECTOR
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/dental-braces.png", width=64)
    st.title("Apex AI Hub")
    st.caption("Multi-Role Demo & Telemetry Inspector")
    st.markdown("---")
    
    selected_role = st.selectbox(
        "🎭 Select Active User View / Persona",
        [
            "💬 Patient WhatsApp View (AI Concierge)",
            "👨‍⚕️ Doctor Command Center (Dr. Chinmay)",
            "👩‍💼 Receptionist Operations Dashboard"
        ]
    )
    
    st.markdown("---")
    current_macro = st.session_state.session_db.get("macro_state", "M1_STATE_LOGISTICS")
    current_intent = st.session_state.session_db.get("last_intent", "INTENT_CLINIC_TIMINGS")
    
    st.markdown(f"**Active State:** <span class='state-badge'>{current_macro}</span>", unsafe_allow_html=True)
    st.markdown(f"**Last Intent:** <span class='intent-badge'>{current_intent}</span>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("🔍 Live MIDGO Memory DB")
    st.json(st.session_state.session_db)
    
    st.markdown("---")
    if st.button("🔄 Reset Patient Session"):
        st.session_state.session_db = {
            "node_id": "Yelahanka_Node_v0.2",
            "macro_state": "M1_STATE_LOGISTICS",
            "last_intent": "INTENT_CLINIC_TIMINGS",
            "name": "",
            "symptom": "",
            "slot_confirmed": False,
            "confirmed_slot": None,
            "check_in_code": None
        }
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Session reset. How can I help you with your dental care at Yelahanka Node today?"
        }]
        log_telemetry_event("SESSION_RESET", {"node_id": "Yelahanka_Node_v0.2"})
        st.rerun()

# ==========================================
# 4. VIEW 1: PATIENT WHATSAPP VIEW
# ==========================================
if selected_role == "💬 Patient WhatsApp View (AI Concierge)":
    st.title("💬 Apex Dental — Patient AI Concierge")
    st.caption("Powered by Gemini 2.5 Flash & TrueLark 30-Intent Finite State Graph")

    # Render chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])

    # Top 5 Fast-Path UI Buttons
    st.markdown("##### ⚡ Quick FAQ Fast-Path Inputs:")
    faq_cols = st.columns(5)
    selected_faq = None

    with faq_cols[0]:
        if st.button("📍 Location & Parking"):
            selected_faq = "Where are you located in Yelahanka and is parking available?"
    with faq_cols[1]:
        if st.button("💳 RCT Cost & Insurance"):
            selected_faq = "How much does a root canal cost and do you take Star Health insurance?"
    with faq_cols[2]:
        if st.button("🦷 Emergency Crown"):
            selected_faq = "My front tooth crown just cracked and it's bleeding!"
    with faq_cols[3]:
        if st.button("🕒 Weekend Hours"):
            selected_faq = "What are your Sunday and weekend timings?"
    with faq_cols[4]:
        if st.button("✨ Implants & Braces"):
            selected_faq = "What are the costs for dental implants and clear aligners?"

    # User Input Handler
    chat_text = st.chat_input("Type your message here...")
    user_input = selected_faq or chat_text

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        current_state = st.session_state.session_db
        
        # System Instruction with 30-Intent Taxonomy
        system_prompt = f"""
        You are 'Apex Assistant', the highly empathetic AI receptionist at Apex Dental Center & Implant Institute, Yelahanka Node v0.2. 
        Your goal is to triage symptoms, answer clinical/FAQ queries, gather the patient's name, and book an appointment slot.

        CURRENT PATIENT MEMORY:
        - Name: "{current_state['name'] or 'Unknown'}"
        - Symptom/Reason: "{current_state['symptom'] or 'Unknown'}"
        - Slot Confirmed: {current_state['slot_confirmed']}

        YELAHANKA NODE v0.2 CLINICAL PROFILE & FAQ:
        - Location: 5th Phase, Yelahanka New Town, Bengaluru (near Major Sandeep Unnikrishnan Road). Free basement valet parking!
        - Operating Hours: Mon-Sat: 09:00 AM - 08:30 PM | Sun: 10:00 AM - 02:00 PM.
        - Languages: English, Kannada, Hindi.
        - Insurance & EMI: HDFC ERGO, Star Health, ICICI Lombard, Max Bupa. 0% interest EMI available for implants/braces!
        - Lead Surgeon: Dr. Chinmay Hudedamani (MDS, Oral & Maxillofacial Surgeon & Implantologist).
        - Pricing: Consult (₹700), Scaling (₹1,500-₹2,500), RCT (₹4,500-₹7,500), Implants (₹25,000-₹45,000), Braces (₹30,000-₹70,000).
        - Crown Warranty: Zirconia (10-15 yr warranty), Implants (Lifetime warranty).
        - Sterilization: Class-B Autoclave 6-step sterilization protocols.

        THE 30 INTENT CLASSIFICATION TAXONOMY:
        You MUST classify the user turn into one of these 30 exact tags:
        - LOGISTICS: INTENT_CONSULT_FEE, INTENT_HOURS_WEEKEND, INTENT_CLINIC_TIMINGS, INTENT_EMERGENCY_BOOKING, INTENT_LANGUAGE_SUPPORT, INTENT_PARKING_VALET, INTENT_TELE_DENTISTRY, INTENT_STERILIZATION_PROTOCOLS
        - FINANCE: INTENT_INSURANCE_CLAIM, INTENT_EMI_PLANS, INTENT_COST_RCT, INTENT_COST_IMPLANTS, INTENT_WARRANTY_CARD
        - PREVENTIVE: INTENT_SCALING_DURATION, INTENT_BLEEDING_GUMS, INTENT_TOOTH_SENSITIVITY, INTENT_DIAGNOSTIC_XRAY, INTENT_RCT_SITTINGS
        - COSMETIC/SURGICAL: INTENT_TEETH_WHITENING, INTENT_ALIGNERS_BRACES, INTENT_ORTHODONTIC_COST, INTENT_WISDOM_EXTRACTION, INTENT_CROWNS_BRIDGES, INTENT_VENEERS_LIFESPAN, INTENT_BRIDGE_VS_IMPLANT, INTENT_DENTURES_ELDERLY, INTENT_LASER_DENTISTRY, INTENT_PEDIATRIC_DENTISTRY
        - EMERGENCY: INTENT_TRAUMA_FIRST_AID, INTENT_POST_OP_CARE

        CRITICAL MIDGO INSTRUCTIONS:
        1. For INTENT_TRAUMA_FIRST_AID: Provide urgent step-by-step first aid (e.g. pressure with clean gauze, preserve knocked tooth in cold milk) and offer an immediate priority emergency slot!
        2. For all other intents: Answer the patient's specific question reassuringly in sentence 1, then smoothly pivot to collecting their missing name or confirming a consultation slot.
        3. Keep `patient_reply` under 3 sentences.
        """

        try:
            ai_client = GeminiMIDGOClient()
            result: MIDGODentalResponse = ai_client.process_turn(system_prompt, user_input)

            intent = result.classified_intent
            macro_info = TAXONOMY_30_INTENTS.get(intent, ("M1_STATE_LOGISTICS", "General Logistics"))
            current_state["last_intent"] = intent
            current_state["macro_state"] = macro_info[0]

            if result.extracted_name and result.extracted_name.lower() not in ["unknown", "none"]:
                current_state["name"] = result.extracted_name
            if result.extracted_symptom_or_reason and result.extracted_symptom_or_reason.lower() not in ["unknown", "none"]:
                current_state["symptom"] = result.extracted_symptom_or_reason

            reply_text = result.patient_reply

            # Handle Emergency Trauma Override
            if intent in ["INTENT_TRAUMA_FIRST_AID", "INTENT_EMERGENCY_BOOKING"]:
                code_num = random.randint(1000, 9999)
                check_in_code = f"APX-EMERGENCY-{code_num}"
                current_state["check_in_code"] = check_in_code
                reply_text += f"\n\n🚨 **URGENT EMERGENCY PRIORITY UNLOCKED**: Check-in code **{check_in_code}**. Please head directly to our Yelahanka 5th Phase clinic or call our emergency desk!"
                log_telemetry_event("EMERGENCY_EXEMPTION_TRIGGERED", {"check_in_code": check_in_code, "symptom": current_state["symptom"]})

            # Handle Slot Selection Flow
            elif current_state["name"] and current_state["symptom"] and not current_state["slot_confirmed"]:
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
                    log_telemetry_event("BOOKING_LOCKED", {"name": current_state["name"], "slot": user_input, "check_in_code": check_in_code})
                else:
                    reply_text += (
                        f" We have available consultation slots tomorrow at Yelahanka for {current_state['name']}: "
                        "• 10:30 AM • 02:00 PM • 04:30 PM. Which works best?"
                    )

            st.session_state.session_db = current_state

            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(reply_text)
            
            st.session_state.messages.append({"role": "assistant", "content": reply_text})

        except Exception as e:
            error_msg = f"⚠️ System notice: Encountered an exception while processing your request ({e}). Please ensure your `GEMINI_API_KEY` is configured correctly in `.env`."
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

# ==========================================
# 5. VIEW 2: DOCTOR COMMAND CENTER
# ==========================================
elif selected_role == "👨‍⚕️ Doctor Command Center (Dr. Chinmay)":
    st.title("👨‍⚕️ Doctor Command Center & Override Suite")
    st.caption("Dr. Chinmay Hudedamani (MDS) — Lead Surgeon & Executive Operations")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Today's Roster", "12 Patients")
    col2.metric("Confirmed Check-Ins", "8 Checked-In")
    col3.metric("Emergency Priority", "1 Critical")
    col4.metric("Estimated Revenue", "₹48,500")

    st.markdown("---")
    st.subheader("📋 Active Today's Patient Roster")
    st.dataframe([
        {"Time": "10:30 AM", "Patient": "Rahul Sharma", "Symptom": "Lower Molar Toothache", "Status": "CONFIRMED", "Check-In Code": "APX-4928"},
        {"Time": "11:15 AM", "Patient": "Priya Nair", "Symptom": "Teeth Whitening Consult", "Status": "CHECKED_IN", "Check-In Code": "APX-8237"},
        {"Time": "02:00 PM", "Patient": "Ananya Roy", "Symptom": "Crown Replacement", "Status": "SLOT_HELD", "Check-In Code": "APX-3912"},
        {"Time": "04:30 PM", "Patient": "Vikram Seth", "Symptom": "Wisdom Tooth Extraction", "Status": "CONFIRMED", "Check-In Code": "APX-9102"},
    ], use_container_width=True)

    st.markdown("---")
    st.subheader("🛠️ Doctor Reschedule & Cancellation Override Tool")
    st.caption("Execute proactive schedule adjustments with custom patient reasons")

    with st.form("doctor_override_form"):
        col_id, col_action = st.columns(2)
        with col_id:
            appt_id = st.text_input("Appointment ID or Check-In Code", value="APX-4928")
        with col_action:
            action_type = st.selectbox("Action Type", ["RESCHEDULE", "CANCEL"])
        
        custom_reason = st.text_area(
            "Custom Medical / Schedule Reason (Required)",
            placeholder="e.g., Doctor called into emergency surgery in OT / Personal family emergency",
            help="This custom reason is logged into AuditLog and sent directly to the patient via WhatsApp notification."
        )
        
        submit_btn = st.form_submit_button("⚡ Execute Schedule Override & Notify Patient")
        
        if submit_btn:
            if not custom_reason or len(custom_reason.strip()) < 5:
                st.error("❌ Error: A detailed custom reason (at least 5 characters) is required.")
            else:
                st.success(f"✅ Action '{action_type}' executed for '{appt_id}'. Patient notified with custom reason: '{custom_reason}'!")
                log_telemetry_event("DOCTOR_OVERRIDE_EXECUTED", {
                    "appointment_id": appt_id,
                    "action_type": action_type,
                    "custom_reason": custom_reason,
                    "doctor": "Dr. Chinmay Hudedamani"
                })

    st.markdown("---")
    st.subheader("💬 Doctor Conversational Assistant")
    for d_msg in st.session_state.doctor_messages:
        with st.chat_message(d_msg["role"], avatar="👨‍⚕️" if d_msg["role"] == "user" else "🤖"):
            st.markdown(d_msg["content"])

    if doc_input := st.chat_input("Ask your AI assistant for patient summaries, roster updates, or revenue details..."):
        st.session_state.doctor_messages.append({"role": "user", "content": doc_input})
        with st.chat_message("user", avatar="👨‍⚕️"):
            st.markdown(doc_input)

        doc_reply = f"Dr. Chinmay, regarding '{doc_input}': Rahul Sharma is scheduled at 10:30 AM for lower molar RCT. All sterilization protocols are verified, and free basement valet parking is active."
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(doc_reply)
        st.session_state.doctor_messages.append({"role": "assistant", "content": doc_reply})

# ==========================================
# 6. VIEW 3: RECEPTIONIST OPERATIONS DASHBOARD
# ==========================================
else:
    st.title("👩‍💼 Receptionist Operations Dashboard")
    st.caption("Apex Dental Center — Yelahanka Node v0.2 Front Desk")

    col1, col2, col3 = st.columns(3)
    col1.metric("Waiting Room", "3 Patients")
    col2.metric("In Consultation", "1 Patient")
    col3.metric("Completed Today", "5 Patients")

    st.markdown("---")
    st.subheader("⚡ Quick Patient Check-In Verifier")
    checkin_code = st.text_input("Enter 6-Character Check-In Code (e.g., APX-4928)")
    
    if st.button("🔍 Verify & Check-In Patient"):
        if checkin_code.upper() in ["APX-4928", "APX-8237", "APX-3912"]:
            st.success(f"✅ Code **{checkin_code.upper()}** Verified! Patient: Rahul Sharma | Slot: 10:30 AM | Dr. Chinmay Hudedamani (Checked In)")
            log_telemetry_event("RECEPTIONIST_CHECKIN_VERIFIED", {"code": checkin_code.upper()})
        else:
            st.warning(f"Searching database for code '{checkin_code.upper()}'... Patient verified for walk-in consultation!")

    st.markdown("---")
    st.subheader("📝 Manual Walk-In Booking Override")
    with st.form("receptionist_walkin_form"):
        w_name = st.text_input("Patient Full Name")
        w_phone = st.text_input("Patient Phone Number (+91)")
        w_symptom = st.text_input("Primary Symptom / Consultation Reason")
        w_slot = st.selectbox("Assign Slot", ["10:30 AM", "02:00 PM", "04:30 PM", "Immediate Emergency Slot"])
        
        if st.form_submit_button("📅 Book Walk-In Patient"):
            if w_name and w_symptom:
                code_val = f"APX-{random.randint(1000, 9999)}"
                st.success(f"✅ Walk-In Appointment Booked! Patient: **{w_name}** | Slot: **{w_slot}** | Check-In Code: **{code_val}**")
                log_telemetry_event("RECEPTIONIST_WALKIN_BOOKED", {"name": w_name, "slot": w_slot, "code": code_val})
            else:
                st.error("❌ Please provide patient name and symptom.")
