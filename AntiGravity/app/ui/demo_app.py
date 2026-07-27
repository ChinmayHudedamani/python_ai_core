# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI / Copus AI — Clean & Reliable WhatsApp Concierge Demo

import streamlit as st
import sys
from pathlib import Path

# Ensure workspace root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.services.session.session_context import SessionContextManager
from app.services.session.models import SaaSPlanTier, PatientSession
from app.services.whatsapp_formatter import WhatsAppFormatter
from app.services.ai_sandwich import AISandwichEngine
from app.ui.reception_cache import ReceptionistDailyCache, OfflineAppointmentRecord
from app.utils.time_utils import get_current_ist, format_ist_time

# Page Configuration
st.set_page_config(
    page_title="Kasthuri Dental Clinic — WhatsApp AI Concierge",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Session State Initialization ---
if "user_phone" not in st.session_state:
    st.session_state.user_phone = "+919876543210"

if "active_tier" not in st.session_state:
    st.session_state.active_tier = SaaSPlanTier.TIER_1

if "session_manager" not in st.session_state:
    st.session_state.session_manager = SessionContextManager()

if "session_state_obj" not in st.session_state:
    st.session_state.session_state_obj = PatientSession(
        session_id="SESS_WA_9912",
        phone_number=st.session_state.user_phone,
        active_tier=st.session_state.active_tier
    )
    st.session_state.session_manager.session_state_obj = st.session_state.session_state_obj

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "sender": "assistant",
            "text": "👋 Welcome to **Kasthuri Dental Clinic**!\nI am Copus, your 24/7 AI Dental Assistant.\n\nHow may we assist you today?"
        }
    ]

if "reception_cache" not in st.session_state:
    cache = ReceptionistDailyCache()
    cache.seed_daily_roster({
        "APX-4928": OfflineAppointmentRecord("APX-4928", "Rahul Kumar", "+919876543210", "Surgical Extraction", "10:30 AM IST", amount_due_inr=1200),
        "APX-8237": OfflineAppointmentRecord("APX-8237", "Priya Sharma", "+919876543211", "Root Canal (RCT)", "11:30 AM IST", amount_due_inr=4500),
    })
    st.session_state.reception_cache = cache

sandwich_engine = AISandwichEngine(st.session_state.session_manager)

# --- SIDEBAR ADMIN CONTROLLER ---
st.sidebar.title("⚙️ SaaS Admin Settings")
selected_tier_str = st.sidebar.selectbox(
    "Active Subscription Tier",
    options=[t.value for t in SaaSPlanTier],
    format_func=lambda x: {
        SaaSPlanTier.TIER_1.value: "🟢 Tier 1: Essential (Menu Bot)",
        SaaSPlanTier.TIER_2.value: "🟡 Tier 2: Pro (Dual Admin Portals)",
        SaaSPlanTier.TIER_2_5_BETA.value: "🧪 Tier 2.5: Beta Testing (Sandbox AI)",
        SaaSPlanTier.TIER_3.value: "🔴 Tier 3: Enterprise (🚀 In Production)"
    }[x],
    index=[t.value for t in SaaSPlanTier].index(st.session_state.active_tier.value)
)

# Handle Tier Switching
new_tier = SaaSPlanTier(selected_tier_str)
if new_tier != st.session_state.active_tier:
    st.session_state.active_tier = new_tier
    st.session_state.session_state_obj.active_tier = new_tier
    st.session_state.session_manager.set_tier(st.session_state.session_state_obj, new_tier)
    st.rerun()

if st.sidebar.button("🔄 Reset WhatsApp Chat", use_container_width=True):
    st.session_state.session_state_obj.reset_hidden_options()
    st.session_state.session_state_obj.is_active = True
    st.session_state.session_state_obj.is_authenticated = False
    st.session_state.session_state_obj.check_in_code = None
    st.session_state.chat_history = [
        {
            "sender": "assistant",
            "text": "👋 Welcome to **Kasthuri Dental Clinic**!\nI am Copus, your 24/7 AI Dental Assistant.\n\nHow may we assist you today?"
        }
    ]
    st.rerun()

st.sidebar.divider()
st.sidebar.caption(f"**Mode**: {st.session_state.active_tier.value}")
st.sidebar.caption(f"**Current IST**: {format_ist_time(get_current_ist())}")

with st.sidebar.expander("🔍 Session Inspector"):
    st.write(f"**Phone**: {st.session_state.user_phone}")
    st.write(f"**Hidden Options**: {list(st.session_state.session_state_obj.hidden_options)}")

# --- MAIN NAVIGATION TABS ---
tab_patient, tab_doctor, tab_reception = st.tabs([
    "💬 WhatsApp Patient Bot",
    "👨‍⚕️ Doctor Portal",
    "👩‍💼 Receptionist Desk"
])

# ==========================================
# TAB 1: SIMPLE & RELIABLE WHATSAPP BOT DEMO
# ==========================================
with tab_patient:
    st.title("💬 Kasthuri Dental Clinic — WhatsApp Assistant")
    st.caption(f"🟢 **Online** | Official Business Account | Mode: **{st.session_state.active_tier.value}**")
    
    if st.session_state.active_tier == SaaSPlanTier.TIER_2_5_BETA:
        st.info("🧪 **Tier 2.5 Beta Mode Active**: Testing Local NLM & Decision Tree Fallback.")
    elif st.session_state.active_tier == SaaSPlanTier.TIER_3:
        st.success("🚀 **Enterprise Mode Active (In Production)**: Gated AI Sandwich Engine Live.")

    st.divider()

    # Render Chat History cleanly using native Streamlit chat bubbles
    for msg in st.session_state.chat_history:
        avatar = "👤" if msg["sender"] == "user" else "🤖"
        with st.chat_message(msg["sender"], avatar=avatar):
            st.markdown(msg["text"])

    st.divider()

    # Interactive Menu Options
    available_menu = st.session_state.session_manager.get_available_menu(st.session_state.session_state_obj)

    if not available_menu:
        st.info("ℹ️ All informational choices viewed. Scroll up to re-read details.")
    else:
        st.subheader("📱 Select an Option:")
        formatted_payload = WhatsAppFormatter.format_menu(available_menu)
        
        # Display Quick Reply Buttons
        cols = st.columns(min(len(formatted_payload.options), 3))
        selected_btn = None
        for idx, option_text in enumerate(formatted_payload.options):
            col = cols[idx % min(len(formatted_payload.options), 3)]
            if col.button(option_text, key=f"btn_{idx}_{option_text}"):
                selected_btn = option_text

        text_input = st.chat_input("Type menu choice, message, or question...")
        user_choice = selected_btn or text_input

        if user_choice:
            st.session_state.chat_history.append({"sender": "user", "text": user_choice})
            
            # Execute option via Multi-Resilient Engine
            command_res = sandwich_engine.process_patient_input(user_choice)
            st.session_state.chat_history.append({"sender": "assistant", "text": command_res.message})
            st.rerun()

# ==========================================
# TAB 2: DOCTOR PORTAL
# ==========================================
with tab_doctor:
    st.title("👨‍⚕️ Doctor Command Center (Dr. Chinmay Hudedamani, MDS)")

    if st.session_state.active_tier == SaaSPlanTier.TIER_1:
        st.warning("🔒 **Tier 2 Pro Upgrade Required**: Doctor Portal is unlocked in Tier 2, Tier 2.5, and Tier 3.")
    else:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Today's Appointments", "12 Patients")
        col2.metric("Confirmed Check-Ins", "8 Verified")
        col3.metric("Emergency Priority", "1 Acute")
        col4.metric("Revenue Protected", "₹48,500")

        st.divider()
        st.subheader("🚨 Proactive OT Emergency Schedule Override")
        with st.form("ot_override_form"):
            affected_slot = st.selectbox("Select OT Slot to Clear", ["11:30 AM – 01:00 PM IST (Surgical)", "03:00 PM – 04:30 PM IST (Implants)"])
            custom_reason = st.text_input("Reason for Override", "Dr. Chinmay called into urgent emergency OT surgery")
            submit = st.form_submit_button("⚡ Issue Reschedule Alerts")

            if submit:
                st.success(f"✅ Proactive alerts dispatched to patients for slot '{affected_slot}'. Reason: '{custom_reason}'. Time: {format_ist_time(get_current_ist())}.")

# ==========================================
# TAB 3: RECEPTIONIST DASHBOARD
# ==========================================
with tab_reception:
    st.title("👩‍💼 Receptionist Desk & Payment Collector")

    if st.session_state.active_tier == SaaSPlanTier.TIER_1:
        st.warning("🔒 **Tier 2 Pro Upgrade Required**: Receptionist Desk is unlocked in Tier 2, Tier 2.5, and Tier 3.")
    else:
        st.subheader("⚡ Patient Check-In & On-the-Spot Payment Collector")
        
        col_code, col_method = st.columns([2, 1])
        with col_code:
            code_input = st.text_input("Enter Patient Check-In Code (`APX-XXXX`):", placeholder="APX-4928").upper()
        with col_method:
            pay_method = st.selectbox("Payment Method", ["UPI (GPay / PhonePe / Paytm)", "Cash", "Credit / Debit Card"])

        if st.button("Verify Patient & Collect Payment"):
            if code_input:
                verification = st.session_state.reception_cache.verify_and_collect_payment(code_input, payment_method=pay_method)
                if verification["status"] == "SUCCESS":
                    st.success(verification["message"])
                elif verification["status"] == "ALREADY_VERIFIED":
                    st.warning(verification["message"])
                else:
                    st.error(verification["message"])
            else:
                st.warning("Please enter a valid 6-character check-in code.")
