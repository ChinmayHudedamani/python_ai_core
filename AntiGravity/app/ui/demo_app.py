# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI / Copus AI — 3-Tier Multi-Role Streamlit Simulator & SaaS Tier Selector

import os
import json
import random
import streamlit as st
from pathlib import Path
import sys

# Ensure workspace root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.services.session.models import PatientSession, SaaSPlanTier, ActionType
from app.services.session.session_context import SessionContextManager
from app.services.tier_config import TIER_CAPABILITIES
from app.services.llm_client import log_telemetry_event
from app.services.whatsapp_formatter import WhatsAppFormatter
from app.ui.reception_cache import verify_checkin_code_offline, DEFAULT_MOCK_ROSTER

# ==========================================
# 1. PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="Apex AI Concierge — 3-Tier SaaS Platform",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stChatFloatingInputContainer {bottom: 20px;}
    .metric-card {background-color: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #e9ecef;}
    .tier-badge {background-color: #e3f2fd; color: #0d47a1; padding: 4px 10px; border-radius: 6px; font-weight: bold;}
    .locked-card {background-color: #fff3e0; border: 1px solid #ffe0b2; padding: 15px; border-radius: 8px; color: #e65100;}
    </style>
""", unsafe_allow_html=True)

# Initialize Session Context Manager
context_mgr = SessionContextManager()

# ==========================================
# 2. SESSION & STATE ENGINE
# ==========================================
if "patient_session" not in st.session_state:
    st.session_state.patient_session = PatientSession(
        session_id="SESS_TEL_9921",
        phone_number="+919876543210",
        active_tier=SaaSPlanTier.TIER_1
    )

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [{
        "role": "assistant",
        "content": (
            "Hey there! 👋 I'm APEX AI Concierge from Apex Dental Center & Implant Institute. 🌿\n\n"
            "Welcome! Please select an option from the menu below to begin."
        )
    }]

# ==========================================
# 3. SIDEBAR: SAAS TIER SELECTOR & TELEMETRY HUB
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/dental-braces.png", width=64)
    st.title("Apex AI SaaS Hub")
    st.caption("Polymorphic Strategy Architecture")
    st.markdown("---")

    # 🎛️ Dynamic SaaS Tier Selector
    st.subheader("🎛️ Active Clinic SaaS Subscription Tier")
    selected_tier_str = st.radio(
        "Select Subscription Level",
        [
            "Tier 1: Essential (24/7 Digital Receptionist)",
            "Tier 2: Pro (Revenue & Schedule Guard)",
            "Tier 3: Enterprise (Apollo/Fortis-Grade Concierge)"
        ]
    )

    # Update active tier in session
    if "Tier 1" in selected_tier_str:
        st.session_state.patient_session.active_tier = SaaSPlanTier.TIER_1
    elif "Tier 2" in selected_tier_str:
        st.session_state.patient_session.active_tier = SaaSPlanTier.TIER_2
    else:
        st.session_state.patient_session.active_tier = SaaSPlanTier.TIER_3

    active_tier = st.session_state.patient_session.active_tier
    tier_info = TIER_CAPABILITIES[active_tier]

    st.markdown(f"**Current Active Strategy:** <span class='tier-badge'>{active_tier.value}</span>", unsafe_allow_html=True)
    st.caption(tier_info["name"])

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
    st.subheader("🔍 Live Patient Memory DB")
    st.json({
        "session_id": st.session_state.patient_session.session_id,
        "phone_number": st.session_state.patient_session.phone_number,
        "active_tier": st.session_state.patient_session.active_tier.value,
        "hidden_options": list(st.session_state.patient_session.hidden_options),
        "is_authenticated": st.session_state.patient_session.is_authenticated,
        "check_in_code": st.session_state.patient_session.check_in_code,
        "is_active": st.session_state.patient_session.is_active
    })

    st.markdown("---")
    if st.button("🔄 Reset Patient Session"):
        st.session_state.patient_session.reset_hidden_options()
        st.session_state.patient_session.is_active = True
        st.session_state.patient_session.is_authenticated = False
        st.session_state.patient_session.check_in_code = None
        st.session_state.chat_messages = [{
            "role": "assistant",
            "content": "Session reset. Welcome to Apex Dental! Select an option below to begin."
        }]
        st.rerun()

# ==========================================
# 4. VIEW 1: PATIENT WHATSAPP VIEW
# ==========================================
if selected_role == "💬 Patient WhatsApp View (AI Concierge)":
    st.title("💬 Apex Dental — Patient WhatsApp AI Concierge")
    st.caption(f"Strategy Engine: {tier_info['name']}")

    # Render chat history
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])

    # Render Available Dynamic Menu Buttons
    available_menu = context_mgr.get_available_menu(st.session_state.patient_session)
    formatted_payload = WhatsAppFormatter.format_menu(available_menu)

    st.markdown("##### 📱 Interactive WhatsApp Menu Payload:")
    st.caption(f"Meta API Payload Type: `{formatted_payload.get('type')}`")

    # Render Menu Choice Buttons
    selected_option = None
    menu_cols = st.columns(min(len(available_menu), 4)) if available_menu else []
    for idx, opt in enumerate(available_menu):
        col = menu_cols[idx % len(menu_cols)]
        with col:
            if st.button(opt, key=f"btn_{idx}_{opt}"):
                selected_option = opt

    # Freeform Input Handler
    chat_text = st.chat_input("Type menu number or response...")
    user_input = selected_option or chat_text

    if user_input:
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        # Handle OTP Verification step in Tier 2 / 3
        if st.session_state.patient_session.otp_code and not st.session_state.patient_session.is_authenticated:
            if user_input.strip() == st.session_state.patient_session.otp_code:
                st.session_state.patient_session.is_authenticated = True
                reply_text = "✅ *MOBILE NUMBER VERIFIED SUCCESSFULLY!* Live slots unlocked. Click '📅 Book Appointment (Live Slots)' to lock your preferred time."
            else:
                reply_text = f"❌ Invalid OTP. Enter the 4-digit code **{st.session_state.patient_session.otp_code}** to authenticate."
        else:
            # Execute command through Strategy Dispatcher Engine
            result = context_mgr.execute_option(st.session_state.patient_session, user_input)
            reply_text = result.message

        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(reply_text)

        st.session_state.chat_messages.append({"role": "assistant", "content": reply_text})
        st.rerun()

# ==========================================
# 5. VIEW 2: DOCTOR COMMAND CENTER
# ==========================================
elif selected_role == "👨‍⚕️ Doctor Command Center (Dr. Chinmay)":
    st.title("👨‍⚕️ Doctor Command Center & OT Override Suite")
    st.caption("Dr. Chinmay Hudedamani (MDS) — Executive Operations")

    if not tier_info["features"].get("has_doctor_command_center", False):
        st.markdown(
            "<div class='locked-card'>"
            "<h3>🔒 Enterprise Feature Locked</h3>"
            "<p>The <b>Doctor Command Center & OT Schedule Override Engine</b> requires <b>Tier 3: Enterprise Subscription</b>.</p>"
            "<p>Switch subscription tier in the sidebar to <b>Tier 3: Enterprise</b> to test this feature!</p>"
            "</div>",
            unsafe_allow_html=True
        )
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Today's Roster", "12 Patients")
        col2.metric("Confirmed Check-Ins", "8 Checked-In")
        col3.metric("Emergency Priority", "1 Critical")

        st.markdown("---")
        st.subheader("📋 Active Patient Roster")
        st.dataframe(DEFAULT_MOCK_ROSTER, use_container_width=True)

        st.markdown("---")
        st.subheader("🛠️ Doctor Reschedule & Cancellation Override Tool")
        with st.form("doc_override"):
            appt_id = st.text_input("Check-In Code", value="APX-4928")
            action = st.selectbox("Action", ["CANCEL", "RESCHEDULE"])
            reason = st.text_area("Custom Medical Reason", value="Doctor called into emergency OT surgery")
            if st.form_submit_button("⚡ Execute & Notify Patient"):
                st.success(f"✅ Action '{action}' executed for '{appt_id}'. Patient notified with reason: '{reason}'!")

# ==========================================
# 6. VIEW 3: RECEPTIONIST OPERATIONS DASHBOARD
# ==========================================
else:
    st.title("👩‍💼 Receptionist Operations Dashboard")
    st.caption("Apex Dental Center — Front Desk Operations")

    col1, col2, col3 = st.columns(3)
    col1.metric("Waiting Room", "3 Patients")
    col2.metric("In Consultation", "1 Patient")
    col3.metric("Completed Today", "5 Patients")

    st.markdown("---")
    st.subheader("⚡ Offline-First Check-In Code Verifier")
    check_code = st.text_input("Enter 6-Character Check-In Code (e.g., APX-4928)")

    if st.button("🔍 Verify Check-In Code (Offline Cache)"):
        res = verify_checkin_code_offline(check_code)
        if res["verified"]:
            st.success(res["message"])
        else:
            st.warning(res["message"])
