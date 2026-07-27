# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI / Copus AI — Dual-Portal & Sandbox Clinic Concierge Frontend Application

import streamlit as st
import sys
from pathlib import Path

# Ensure workspace root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.services.session.session_context import SessionContextManager
from app.services.session.models import SaaSPlanTier, ActionType, PatientSession
from app.services.whatsapp_formatter import WhatsAppFormatter
from app.services.care_card_service import CareCardService, ProcedureCategory
from app.ui.reception_cache import ReceptionistDailyCache, OfflineAppointmentRecord

# Page Configuration
st.set_page_config(
    page_title="APEX AI — Clinic Concierge Hub",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Glassmorphism CSS
CUSTOM_CSS = """
<style>
    .stApp {
        background-color: #f4f6f8;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .lock-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(8px);
        border-left: 6px solid #ff9800;
        border-radius: 8px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        color: #e65100;
    }
    .beta-card {
        background: rgba(255, 248, 225, 0.95);
        backdrop-filter: blur(8px);
        border-left: 6px solid #f57c00;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(245, 124, 0, 0.1);
        color: #e65100;
    }
    .production-card {
        background: rgba(235, 243, 255, 0.95);
        backdrop-filter: blur(8px);
        border-left: 6px solid #0F52BA;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(15, 82, 186, 0.1);
        color: #0d47a1;
    }
    div[data-testid="stMetricValue"] {
        font-size: 24px;
        font-weight: 700;
        color: #0F52BA;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# --- Session State Initialization ---
if "user_phone" not in st.session_state:
    st.session_state.user_phone = "+919876543210"

if "active_tier" not in st.session_state:
    st.session_state.active_tier = SaaSPlanTier.TIER_1

if "session_manager" not in st.session_state:
    st.session_state.session_manager = SessionContextManager()

if "session_state_obj" not in st.session_state:
    st.session_state.session_state_obj = PatientSession(
        session_id="SESS_WEB_9912",
        phone_number=st.session_state.user_phone,
        active_tier=st.session_state.active_tier
    )

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"sender": "assistant", "text": "Hello! I am Copus, the Kasthuri Dental Clinic AI assistant. How may I help you today?"}
    ]

if "reception_cache" not in st.session_state:
    cache = ReceptionistDailyCache()
    cache.seed_daily_roster({
        "APX-4928": OfflineAppointmentRecord("APX-4928", "Rahul Kumar", "+919876543210", "Surgical Extraction", "10:30 AM"),
        "APX-8237": OfflineAppointmentRecord("APX-8237", "Priya Sharma", "+919876543211", "Root Canal (RCT)", "11:30 AM"),
    })
    st.session_state.reception_cache = cache

# --- SIDEBAR ADMIN CONTROLLER ---
st.sidebar.image("https://img.icons8.com/color/96/dental-braces.png", width=64)
st.sidebar.title("🛠️ APEX SaaS Admin Panel")
selected_tier_str = st.sidebar.selectbox(
    "Active SaaS Plan Tier",
    options=[t.value for t in SaaSPlanTier],
    format_func=lambda x: {
        SaaSPlanTier.TIER_1.value: "🟢 Tier 1: Essential (Menu Bot)",
        SaaSPlanTier.TIER_2.value: "🟡 Tier 2: Pro (Dual Admin Portals)",
        SaaSPlanTier.TIER_2_5_BETA.value: "🧪 Tier 2.5: Beta Testing (Pre-Triage & Care Cards)",
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

if st.sidebar.button("🔄 Reset Patient Session", use_container_width=True):
    st.session_state.session_state_obj.reset_hidden_options()
    st.session_state.session_state_obj.is_active = True
    st.session_state.session_state_obj.is_authenticated = False
    st.session_state.session_state_obj.check_in_code = None
    st.session_state.chat_history = [
        {"sender": "assistant", "text": "Hello! I am Copus, the Kasthuri Dental Clinic AI assistant. How may I help you today?"}
    ]
    st.rerun()

# Inspector
with st.sidebar.expander("🔍 Session State Inspector"):
    st.write(f"**Phone**: {st.session_state.user_phone}")
    st.write(f"**Active Tier**: {st.session_state.active_tier.value}")
    st.write(f"**Hidden Options**: {list(st.session_state.session_state_obj.hidden_options)}")

# --- MAIN LAYOUT TABS ---
tab_patient, tab_doctor, tab_reception = st.tabs([
    "💬 Patient WhatsApp View",
    "👨‍⚕️ Doctor Command Center",
    "👩‍💼 Receptionist Dashboard"
])

# ==========================================
# TAB 1: PATIENT WHATSAPP SIMULATOR
# ==========================================
with tab_patient:
    st.title("💬 WhatsApp Interactive Concierge")
    
    if st.session_state.active_tier == SaaSPlanTier.TIER_2_5_BETA:
        st.markdown(
            """
            <div class="beta-card">
                <b>🧪 Tier 2.5 Beta Testing Active</b><br/>
                <b>Sandbox Active</b>: Testing Guided Clinical Pre-Triage & Digital Care Cards without full Enterprise infrastructure.
            </div>
            """,
            unsafe_allow_html=True
        )
    elif st.session_state.active_tier == SaaSPlanTier.TIER_3:
        st.markdown(
            """
            <div class="production-card">
                <b>🚀 Enterprise Mode Active (In Production)</b><br/>
                Full Multi-Branch Auto-Router, Cashless TPA Insurance Desk, & Pre-Triage Trees are live.
            </div>
            """,
            unsafe_allow_html=True
        )

    st.caption(f"Connected to **Kasthuri Dental Clinic** | Mode: **{st.session_state.active_tier.value}**")

    # Render Chat Log
    for message in st.session_state.chat_history:
        with st.chat_message(message["sender"], avatar="🤖" if message["sender"] == "assistant" else "👤"):
            st.markdown(message["text"])

    st.divider()

    # Get Filtered Menu
    available_menu = st.session_state.session_manager.get_available_menu(st.session_state.session_state_obj)

    if not available_menu:
        st.info("ℹ️ All informational choices viewed. Scroll up in WhatsApp to re-read past details.")
    else:
        st.subheader("📱 Select an option below:")
        
        # Meta API Sanitizer
        formatted_payload = WhatsAppFormatter.format_menu(available_menu)
        
        cols = st.columns(min(len(formatted_payload.options), 3))
        selected_btn = None
        for idx, option_text in enumerate(formatted_payload.options):
            col = cols[idx % min(len(formatted_payload.options), 3)]
            if col.button(option_text, key=f"btn_{idx}_{option_text}"):
                selected_btn = option_text

        text_input = st.chat_input("Type menu number or response...")
        user_choice = selected_btn or text_input

        if user_choice:
            st.session_state.chat_history.append({"sender": "user", "text": user_choice})
            
            # OTP Verification step in Tier 2/2.5/3
            if st.session_state.session_state_obj.otp_code and not st.session_state.session_state_obj.is_authenticated:
                if user_choice.strip() == st.session_state.session_state_obj.otp_code:
                    st.session_state.session_state_obj.is_authenticated = True
                    reply_text = "✅ *MOBILE NUMBER VERIFIED SUCCESSFULLY!* Live slots unlocked. Click '📅 Book Appointment (Live Slots)' to lock your preferred time."
                else:
                    reply_text = f"❌ Invalid OTP. Enter the 4-digit code **{st.session_state.session_state_obj.otp_code}** to authenticate."
            else:
                # Polymorphic Dispatcher Execution
                command_res = st.session_state.session_manager.execute_option(st.session_state.session_state_obj, user_choice)
                reply_text = command_res.message
            
            st.session_state.chat_history.append({"sender": "assistant", "text": reply_text})
            st.rerun()

# ==========================================
# TAB 2: DOCTOR COMMAND CENTER (UNLOCKED IN TIER 2, TIER 2.5 & TIER 3)
# ==========================================
with tab_doctor:
    st.title("👨‍⚕️ Doctor Command Center (Dr. Chinmay Hudedamani, MDS)")

    # Unlocked in Tier 2, Tier 2.5, and Tier 3!
    if st.session_state.active_tier == SaaSPlanTier.TIER_1:
        st.markdown(
            """
            <div class="lock-card">
                <h3>🔒 Tier 2 Pro Upgrade Required</h3>
                <p>The Doctor Command Center, OT Emergency Override Tool, and Schedule Analytics require Tier 2 (Pro), Tier 2.5 (Beta), or Tier 3 (Enterprise).</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Today's Roster", "12 Patients")
        col2.metric("Confirmed Check-Ins", "8 Verified")
        col3.metric("Emergency Priority", "1 Acute")
        col4.metric("Revenue Protected", "₹48,500")

        st.divider()
        st.subheader("🚨 Proactive OT Emergency Schedule Override")
        with st.form("ot_override_form"):
            affected_slot = st.selectbox("Select OT Slot to Clear", ["11:30 AM – 01:00 PM (Surgical)", "03:00 PM – 04:30 PM (Implants)"])
            custom_reason = st.text_input("Reason for Override", "Dr. Chinmay called into urgent OT surgery")
            submit = st.form_submit_button("⚡ Issue Proactive Reschedule Alerts")

            if submit:
                st.success(f"✅ Proactive alerts dispatched to patients for slot '{affected_slot}'. Reason logged: '{custom_reason}'.")

# ==========================================
# TAB 3: RECEPTIONIST DASHBOARD
# ==========================================
with tab_reception:
    st.title("👩‍💼 Receptionist Operations & Waiting-Room Desk")

    if st.session_state.active_tier == SaaSPlanTier.TIER_1:
        st.markdown(
            """
            <div class="lock-card">
                <h3>🔒 Tier 2 Pro Upgrade Required</h3>
                <p>Check-In Code verification (<code>APX-XXXX</code>) and waiting-room roster management require Tier 2, Tier 2.5, or Tier 3.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.subheader("⚡ Offline-First Check-In Code Verifier")
        code_input = st.text_input("Enter Patient 6-Character Check-In Code (`APX-XXXX`):", placeholder="APX-4928").upper()

        if st.button("Verify Arriving Patient"):
            if code_input:
                verification = st.session_state.reception_cache.verify_checkin_code(code_input)
                if verification["status"] == "SUCCESS":
                    st.success(verification["message"])
                else:
                    st.error(verification["message"])
            else:
                st.warning("Please enter a valid check-in code.")
