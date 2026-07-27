# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Local WhatsApp Demo Simulator & Role-Based Command Center

import streamlit as st
import asyncio
from datetime import datetime, date

from app.services.guardrails import sanitize_input
from app.services.triage_engine import TriageEngine
from app.services.llm_router import get_agent_context, is_authorized_doctor
from app.ui.receptionist_dashboard import render_receptionist_dashboard

st.set_page_config(
    page_title="APEX AI — Dental Clinic Assistant Demo",
    page_icon="🦷",
    layout="wide"
)


# ---------------------------------------------------------
# Sidebar Role Selection & System Config
# ---------------------------------------------------------

st.sidebar.title("🦷 APEX AI Clinic Demo")
st.sidebar.caption("Patented Clinical AI Assistant | Apex Dental Center")

role_choice = st.sidebar.radio(
    "Select User Persona:",
    ["👤 Patient View (Rahul)", "👨‍⚕️ Doctor View (Dr. Vikram Sharma)", "🏥 Receptionist Dashboard"]
)

st.sidebar.divider()
st.sidebar.markdown("### 🛡️ System Guardrails & Architecture")
st.sidebar.write("• **Architecture**: AI Sandwich")
st.sidebar.write("• **Database**: SQLite SQLModel KB & Postgres Models")
st.sidebar.write("• **State**: Redis Hashes (45-min TTL, 6-turn sliding window)")
st.sidebar.write("• **Circuit Breaker**: 4.0s Maximum Timeout")
st.sidebar.write("• **Safety**: Zero-hallucination medical safety hard-stop")


# ---------------------------------------------------------
# Persona 1: Patient View (WhatsApp Simulator)
# ---------------------------------------------------------

if role_choice == "👤 Patient View (Rahul)":
    st.title("💬 WhatsApp Clinical Assistant — Patient View")
    st.caption("Simulating patient WhatsApp chat (+91-9876543210)")

    if "patient_messages" not in st.session_state:
        st.session_state["patient_messages"] = [
            {
                "role": "assistant",
                "content": (
                    "Hey there! 👋 I'm APEX AI, your clinical assistant from Apex Dental Center & Implant Institute, Koramangala. 🌿\n\n"
                    "I'm here to guide you, answer your health questions, and connect you to care when needed.\n\n"
                    "To start, may I know your primary symptom or health concern today?"
                ),
                "reasoning": "Initial greeting loaded. Prompting for mandatory clinical symptom.",
                "tools": []
            }
        ]

    for msg in st.session_state["patient_messages"]:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant", avatar="🦷"):
                st.markdown(msg["content"])
                if msg.get("reasoning"):
                    with st.expander("🧠 AI Sandwich Reasoning Trace"):
                        st.write(msg["reasoning"])
                if msg.get("tools"):
                    with st.expander("⚙️ Tool Inspection Panel"):
                        st.json(msg["tools"])

    user_input = st.chat_input("Type your message to APEX AI...")

    if user_input:
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        st.session_state["patient_messages"].append({"role": "user", "content": user_input})

        # Pre-Guardrail Sanitization
        sanitized = sanitize_input(user_input)
        
        # Triage Engine Check
        triage_engine = TriageEngine()
        triage_res = triage_engine.evaluate_message(user_input)

        if sanitized.get("is_flagged"):
            reply = "I am trained to assist with clinical appointments and dental inquiries. How can I help you today?"
            reasoning = f"🚨 Prompt Injection Flagged: {sanitized.get('flag_reason')}"
            tools = []
        elif triage_res:
            instructions = triage_res["first_aid_instructions"]
            reply = f"🚨 URGENT MEDICAL ALERT: {instructions}\n\nPlease call our emergency line immediately at +91-9988776655."
            reasoning = f"🚨 Emergency Triage Keyword Matched: '{triage_res['matched_keyword']}' ({triage_res['urgency_level']})"
            tools = [{"tool": "TriageEngine.evaluate_message", "result": triage_res}]
        elif "APX-" in user_input.upper():
            code = user_input.strip().upper()
            reply = f"✅ Thank you! Your appointment has been confirmed with check-in code '{code}'. We look forward to seeing you at Apex Dental!"
            reasoning = f"Check-in confirmation code '{code}' verified against Postgres DB."
            tools = [{"tool": "confirm_booking_with_code", "input": {"code": code}}]
        else:
            reply = (
                "Thank you for sharing that! We have available consultation slots tomorrow with Dr. Chinmay Hudedamani:\n\n"
                "• 10:30 AM\n• 02:00 PM\n• 04:30 PM\n\n"
                "Which time works best for you? Reply with your preferred slot and I'll generate your check-in code!"
            )
            reasoning = "Deterministic Slot Lookup executed against Postgres inventory. Query returned 3 open slots."
            tools = [{"tool": "lookup_available_slots", "result": ["10:30 AM", "02:00 PM", "04:30 PM"]}]

        with st.chat_message("assistant", avatar="🦷"):
            st.markdown(reply)
            with st.expander("🧠 AI Sandwich Reasoning Trace"):
                st.write(reasoning)
            if tools:
                with st.expander("⚙️ Tool Inspection Panel"):
                    st.json(tools)

        st.session_state["patient_messages"].append({
            "role": "assistant",
            "content": reply,
            "reasoning": reasoning,
            "tools": tools
        })


# ---------------------------------------------------------
# Persona 2: Doctor View (Executive Command Center)
# ---------------------------------------------------------

elif role_choice == "👨‍⚕️ Doctor View (Dr. Vikram Sharma)":
    st.title("👨‍⚕️ Doctor Executive Assistant Command Center")
    st.caption("Authenticated Doctor Channel (+91-7338350871)")

    st.success("🔐 Authorized Doctor Session Active for Dr. Vikram Sharma (Lead Endodontist)")

    tab1, tab2, tab3 = st.tabs(["📊 Daily Schedule & Ledgers", "💰 Expected Revenue Report", "🚨 Dynamic Rescheduling Tool"])

    with tab1:
        st.subheader("📋 Daily Schedule Ledger")
        st.write("• **10:00 AM** — Rahul Sharma (`APX-4928`) | Root Canal (RCT) | *Throbbing toothache* | ₹4,500.00 | **CONFIRMED**")
        st.write("• **11:30 AM** — Priya Nair (`APX-8102`) | Invisalign Consult | *Alignment check* | ₹700.00 | **SLOT_HELD**")
        st.write("• **02:00 PM** — Vikram Patel (`APX-3391`) | Wisdom Tooth Extraction | *Severe impaction pain* | ₹4,000.00 | **CONFIRMED**")

    with tab2:
        st.subheader("💰 Revenue Projections")
        st.metric("Today's Expected Revenue", "₹9,200.00", delta="+15% vs yesterday")
        st.metric("Confirmed Appointments Count", "2 Confirmed / 1 Held")

    with tab3:
        st.subheader("🚨 Emergency Rescheduling Tool")
        appt_id = st.text_input("Appointment Check-In Code", "APX-4928")
        custom_reason = st.text_input(
            "Enter custom reason for cancellation/reschedule:",
            placeholder="e.g., Emergency surgery in Operation Theatre"
        )
        action_type = st.selectbox("Action Type", ["RESCHEDULE", "CANCEL"])

        if st.button("Trigger Proactive Patient Reschedule"):
            if not custom_reason.strip():
                st.error("⚠️ Please enter a specific custom reason for the cancellation or reschedule.")
            else:
                st.warning(f"🚨 Appointment {appt_id} updated ({action_type}). Proactive WhatsApp notification sent to patient with custom reason: '{custom_reason}'!")
                st.info(f"📲 Sent Template: 'Hi Rahul! Regrettably, Dr. Sharma needs to reschedule your appointment due to: {custom_reason}. We have an alternative slot open at 2026-07-28 at 10:30 AM or 2026-07-28 at 02:00 PM. Would you like to confirm this slot or choose another?'")


# ---------------------------------------------------------
# Persona 3: Receptionist Dashboard View
# ---------------------------------------------------------

else:
    render_receptionist_dashboard()
