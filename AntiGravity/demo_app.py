# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Local WhatsApp Demo Simulator & Interactive Button Command Center

import streamlit as st
import asyncio
import time
from datetime import datetime, date

from app.services.guardrails import sanitize_input
from app.services.triage_engine import TriageEngine
from app.services.normalizers import augment_short_text
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
st.sidebar.write("• **Conversational Flow**: Flexible Human-Like Dialogue Router")
st.sidebar.write("• **Circuit Breaker**: 4.0s Maximum Timeout")
st.sidebar.write("• **Safety**: Zero-hallucination medical safety hard-stop")


# ---------------------------------------------------------
# Persona 1: Patient View (WhatsApp Simulator with Context Badges)
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
                "tools": [],
                "available_slots": [],
                "latency_ms": 1.2
            }
        ]

    for idx, msg in enumerate(st.session_state["patient_messages"]):
        if msg["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(msg["content"])
                if msg.get("context_badge"):
                    st.info(msg["context_badge"])
        else:
            with st.chat_message("assistant", avatar="🦷"):
                st.markdown(msg["content"])

                # Render Interactive Slot Buttons if present
                if msg.get("available_slots"):
                    st.write("**Click to select an appointment slot:**")
                    cols = st.columns(len(msg["available_slots"]))
                    for col_idx, slot in enumerate(msg["available_slots"]):
                        with cols[col_idx]:
                            btn_label = f"📅 {slot['time']}"
                            if st.button(btn_label, key=f"slot_btn_{idx}_{col_idx}"):
                                st.session_state["selected_slot_time"] = slot['time']
                                st.rerun()

                if msg.get("reasoning"):
                    with st.expander(f"🧠 AI Sandwich Reasoning Trace ({msg.get('latency_ms', 0):.1f}ms)"):
                        st.write(msg["reasoning"])
                if msg.get("tools"):
                    with st.expander("⚙️ Tool Inspection Panel"):
                        st.json(msg["tools"])

    # Handle slot button selection
    selected_time = st.session_state.pop("selected_slot_time", None)
    raw_user_input = st.chat_input("Type your message to APEX AI...") or selected_time

    if raw_user_input:
        start_t = time.time()
        
        mock_session_state = {
            "last_intent": "SELECTING_SLOT",
            "last_topic": "Root Canal",
            "pending_code": "APX-4928"
        }
        aug_res = augment_short_text(raw_user_input, mock_session_state)
        
        user_input = aug_res["augmented_text"]
        context_badge = f"💡 [Context Injection] User: '{raw_user_input}' -> Expanded: '{user_input}' ({aug_res.get('applied_rule')})" if aug_res.get("was_augmented") else None

        with st.chat_message("user", avatar="👤"):
            st.markdown(raw_user_input if not aug_res["was_augmented"] else f"{raw_user_input} *(Expanded: '{user_input}')*")
            if context_badge:
                st.info(context_badge)

        st.session_state["patient_messages"].append({
            "role": "user",
            "content": raw_user_input,
            "context_badge": context_badge
        })

        sanitized = sanitize_input(user_input)
        triage_engine = TriageEngine()
        triage_res = triage_engine.evaluate_message(user_input)

        slots_to_render = []
        lower_raw = raw_user_input.lower()

        # Side Inquiries Check (Medications, Painkillers, Directions, Parking)
        if any(w in lower_raw for w in ["tablet", "tablets", "medicine", "medication", "painkiller", "paracetamol", "brufen"]):
            reply = (
                "I understand you're looking for relief! 🌿 However, for your safety, specific medication or painkillers "
                "can only be prescribed directly by Dr. Sharma or Dr. Nair after a proper clinical evaluation.\n\n"
                "In the meantime, you can rinse gently with warm salt water. Would you like me to book your consultation slot for tomorrow?"
            )
            reasoning = "Side Inquiry Intercepted: Medication request flagged. Enforced Legal Safety Rule (No prescribing without clinical evaluation)."
            tools = []
        elif any(w in lower_raw for w in ["parking", "valet", "direction", "address", "location"]):
            reply = (
                "We are located at 104, 80 Feet Road, 4th Block, Koramangala (near Sony World Signal). 🚗\n\n"
                "Yes, we have free basement valet parking available for all patients! Would you like to pick a time slot for your visit?"
            )
            reasoning = "Side Inquiry Intercepted: Location/Parking question answered from SQLite Knowledge Base."
            tools = [{"tool": "ClinicProfile.get_metadata", "result": {"parking": "Free basement valet parking available"}}]
        elif sanitized.get("is_flagged"):
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
        elif any(t in user_input.lower() for t in ["10:30", "02:00", "04:30", "1", "2", "3", "first", "second", "third", "yes, confirm"]):
            reply = (
                f"✅ Selected slot reserved!\n\n"
                f"Your unique check-in code is **APX-4928**.\n"
                f"Please reply with **APX-4928** to confirm your slot!"
            )
            reasoning = f"Context Augmentation & Slot Interceptor matched input '{user_input}'. Reserved slot APX-4928."
            tools = [{"tool": "create_booking", "result": {"check_in_code": "APX-4928", "status": "SLOT_HELD"}}]
        else:
            slots_to_render = [
                {"time": "10:30 AM", "slot_id": "slot-001"},
                {"time": "02:00 PM", "slot_id": "slot-002"},
                {"time": "04:30 PM", "slot_id": "slot-003"}
            ]
            reply = (
                "Thank you for sharing that! We have available consultation slots tomorrow with Dr. Chinmay Hudedamani:\n\n"
                "• 10:30 AM\n• 02:00 PM\n• 04:30 PM\n\n"
                "Click a button below or type your preferred time to reserve your slot!"
            )
            reasoning = "Deterministic Slot Lookup executed against Postgres inventory. Returned 3 open slots and cached in Redis."
            tools = [{"tool": "lookup_available_slots", "result": slots_to_render}]

        end_t = time.time()
        latency_ms = (end_t - start_t) * 1000

        with st.chat_message("assistant", avatar="🦷"):
            st.markdown(reply)
            if slots_to_render:
                st.write("**Click to select an appointment slot:**")
                cols = st.columns(len(slots_to_render))
                for col_idx, slot in enumerate(slots_to_render):
                    with cols[col_idx]:
                        if st.button(f"📅 {slot['time']}", key=f"new_slot_btn_{col_idx}"):
                            st.session_state["selected_slot_time"] = slot['time']
                            st.rerun()

            with st.expander(f"🧠 AI Sandwich Reasoning Trace ({latency_ms:.1f}ms)"):
                st.write(reasoning)
            if tools:
                with st.expander("⚙️ Tool Inspection Panel"):
                    st.json(tools)

        st.session_state["patient_messages"].append({
            "role": "assistant",
            "content": reply,
            "reasoning": reasoning,
            "tools": tools,
            "available_slots": slots_to_render,
            "latency_ms": latency_ms
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
