# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI / Copus AI — Authentic WhatsApp Web UI & Dual-Portal Concierge

import streamlit as st
import sys
from pathlib import Path

# Ensure workspace root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.services.session.session_context import SessionContextManager
from app.services.session.models import SaaSPlanTier, ActionType, PatientSession
from app.services.whatsapp_formatter import WhatsAppFormatter
from app.services.ai_sandwich import AISandwichEngine
from app.services.security import RateLimiter
from app.ui.reception_cache import ReceptionistDailyCache, OfflineAppointmentRecord
from app.utils.time_utils import get_current_ist, format_ist_time

# Page Configuration
st.set_page_config(
    page_title="Kasthuri Dental Clinic — WhatsApp Concierge",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- AUTHENTIC WHATSAPP WEB CSS STYLING (FORCED LIGHT MODE & HIGH CONTRAST) ---
WHATSAPP_CSS = """
<style>
    /* Force Light Mode Color Palette Across All Elements */
    :root {
        --background-color: #efeae2 !important;
        --secondary-background-color: #ffffff !important;
        --text-color: #111b21 !important;
    }

    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #efeae2 !important;
        color: #111b21 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }

    /* Force all text in st.markdown to be dark black/grey */
    p, span, div, h1, h2, h3, h4, h5, h6, label {
        color: #111b21 !important;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #d1d7db !important;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] div, [data-testid="stSidebar"] label {
        color: #111b21 !important;
    }

    /* WhatsApp Header Bar */
    .wa-header {
        background-color: #075e54 !important;
        color: #ffffff !important;
        padding: 14px 18px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid #128c7e;
        border-radius: 8px 8px 0 0;
        margin-bottom: 12px;
    }
    .wa-avatar {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background-color: #ffffff !important;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        margin-right: 12px;
        float: left;
    }
    .wa-title-box {
        float: left;
    }
    .wa-clinic-name {
        font-size: 16px;
        font-weight: 700;
        margin: 0;
        color: #ffffff !important;
    }
    .wa-status {
        font-size: 12px;
        color: #25d366 !important;
        margin: 0;
        font-weight: 500;
    }
    .wa-verified-badge {
        color: #34b7f1 !important;
        font-size: 14px;
        margin-left: 4px;
    }

    /* WhatsApp Message Bubbles */
    .wa-msg-user {
        background-color: #d9fdd3 !important;
        color: #111b21 !important;
        padding: 12px 16px;
        border-radius: 8px 8px 0px 8px;
        max-width: 75%;
        margin-left: auto;
        margin-top: 8px;
        margin-bottom: 8px;
        box-shadow: 0 1px 2px rgba(11, 20, 26, 0.15);
        font-size: 15px;
        line-height: 1.45;
        position: relative;
        word-wrap: break-word;
    }
    .wa-msg-user * {
        color: #111b21 !important;
    }
    
    .wa-msg-bot {
        background-color: #ffffff !important;
        color: #111b21 !important;
        padding: 12px 16px;
        border-radius: 8px 8px 8px 0px;
        max-width: 80%;
        margin-right: auto;
        margin-top: 8px;
        margin-bottom: 8px;
        box-shadow: 0 1px 2px rgba(11, 20, 26, 0.15);
        font-size: 15px;
        line-height: 1.45;
        position: relative;
        word-wrap: break-word;
    }
    .wa-msg-bot * {
        color: #111b21 !important;
    }

    .wa-timestamp {
        font-size: 11px;
        color: #667781 !important;
        float: right;
        margin-top: 4px;
        margin-left: 8px;
    }

    .wa-ticks {
        color: #53bdeb !important;
        font-weight: bold;
        font-size: 12px;
        margin-left: 2px;
    }

    /* Meta WhatsApp Interactive Buttons */
    .stButton > button {
        background-color: #ffffff !important;
        color: #00a884 !important;
        border: 1px solid #c0c7d1 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        padding: 12px 18px !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08) !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        text-align: center !important;
    }

    .stButton > button:hover {
        background-color: #e7f7f3 !important;
        border-color: #00a884 !important;
        color: #075e54 !important;
    }

    /* Admin Cards */
    .lock-card {
        background: #ffffff !important;
        border-left: 6px solid #ff9800;
        border-radius: 8px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        color: #e65100 !important;
    }
    .lock-card * {
        color: #e65100 !important;
    }
    .beta-card {
        background: #fff8e1 !important;
        border-left: 6px solid #f57c00;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 16px;
        color: #e65100 !important;
    }
    .beta-card * {
        color: #e65100 !important;
    }
    .production-card {
        background: #eef4ff !important;
        border-left: 6px solid #0F52BA;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 16px;
        color: #0d47a1 !important;
    }
    .production-card * {
        color: #0d47a1 !important;
    }
    .security-badge {
        background: #e8f5e9 !important;
        border: 1px solid #66bb6a;
        color: #1b5e20 !important;
        border-radius: 6px;
        padding: 6px 12px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
        margin-right: 6px;
        margin-bottom: 6px;
    }
</style>
"""
st.markdown(WHATSAPP_CSS, unsafe_allow_html=True)

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
            "text": "👋 Welcome to Kasthuri Dental Clinic!\nI am Copus, your 24/7 AI Dental Assistant.\n\nHow may we assist you today?",
            "time": "09:00 AM"
        }
    ]

if "reception_cache" not in st.session_state:
    cache = ReceptionistDailyCache()
    cache.seed_daily_roster({
        "APX-4928": OfflineAppointmentRecord("APX-4928", "Rahul Kumar", "+919876543210", "Surgical Extraction", "10:30 AM IST", amount_due_inr=1200),
        "APX-8237": OfflineAppointmentRecord("APX-8237", "Priya Sharma", "+919876543211", "Root Canal (RCT)", "11:30 AM IST", amount_due_inr=4500),
    })
    st.session_state.reception_cache = cache

if "rate_limiter" not in st.session_state:
    st.session_state.rate_limiter = RateLimiter(max_requests=15, window_seconds=60)

sandwich_engine = AISandwichEngine(st.session_state.session_manager)

# --- SIDEBAR ADMIN CONTROLLER ---
st.sidebar.markdown("## ⚙️ SaaS Admin Controls")
selected_tier_str = st.sidebar.selectbox(
    "Active SaaS Subscription Plan",
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

if st.sidebar.button("🔄 Reset WhatsApp Chat Session", use_container_width=True):
    st.session_state.session_state_obj.reset_hidden_options()
    st.session_state.session_state_obj.is_active = True
    st.session_state.session_state_obj.is_authenticated = False
    st.session_state.session_state_obj.check_in_code = None
    st.session_state.chat_history = [
        {
            "sender": "assistant",
            "text": "👋 Welcome to Kasthuri Dental Clinic!\nI am Copus, your 24/7 AI Dental Assistant.\n\nHow may we assist you today?",
            "time": "09:00 AM"
        }
    ]
    st.rerun()

st.sidebar.divider()
st.sidebar.subheader("🛡️ Enterprise Security Badges")
st.sidebar.markdown(
    """
    <div>
        <span class="security-badge">🔒 Distributed Mutex Active</span><br/>
        <span class="security-badge">🛡️ HMAC SHA-256 Verified</span><br/>
        <span class="security-badge">⚡ Max Token Bound: 128 chars</span><br/>
        <span class="security-badge">⏱️ Timezone: Asia/Kolkata (IST)</span>
    </div>
    """,
    unsafe_allow_html=True
)

with st.sidebar.expander("🔍 Session State Inspector"):
    st.write(f"**Phone**: {st.session_state.user_phone}")
    st.write(f"**Tier**: {st.session_state.active_tier.value}")
    st.write(f"**Hidden Items**: {list(st.session_state.session_state_obj.hidden_options)}")

# --- MAIN LAYOUT TABS ---
tab_patient, tab_doctor, tab_reception = st.tabs([
    "💬 WhatsApp Patient Interface",
    "👨‍⚕️ Doctor Command Center",
    "👩‍💼 Receptionist Dashboard"
])

# ==========================================
# TAB 1: AUTHENTIC WHATSAPP WEB SIMULATOR
# ==========================================
with tab_patient:
    
    if st.session_state.active_tier == SaaSPlanTier.TIER_2_5_BETA:
        st.markdown(
            """
            <div class="beta-card">
                <b>🧪 Tier 2.5 Beta Mode Active</b> | Sandbox Local NLM Engine & Branch-and-Bound Fallback.
            </div>
            """,
            unsafe_allow_html=True
        )
    elif st.session_state.active_tier == SaaSPlanTier.TIER_3:
        st.markdown(
            """
            <div class="production-card">
                <b>🚀 Enterprise Mode Active (In Production)</b> | Full Gated AI Sandwich Architecture.
            </div>
            """,
            unsafe_allow_html=True
        )

    # --- WHATSAPP HEADER BAR ---
    st.markdown(
        f"""
        <div class="wa-header">
            <div style="display: flex; align-items: center;">
                <div class="wa-avatar">🦷</div>
                <div class="wa-title-box">
                    <div class="wa-clinic-name">Kasthuri Dental Clinic <span class="wa-verified-badge">☑️</span></div>
                    <div class="wa-status">online • Official Business Account</div>
                </div>
            </div>
            <div style="font-size: 13px; color: #ffffff;">{st.session_state.active_tier.value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Render WhatsApp Chat Messages
    for msg in st.session_state.chat_history:
        msg_time = msg.get("time", "Just now")
        msg_html = msg["text"].replace("\n", "<br/>")
        
        if msg["sender"] == "user":
            st.markdown(
                f"""
                <div class="wa-msg-user">
                    {msg_html}
                    <div class="wa-timestamp">{msg_time} <span class="wa-ticks">✓✓</span></div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div class="wa-msg-bot">
                    {msg_html}
                    <div class="wa-timestamp">{msg_time}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.divider()

    # WhatsApp Interactive Menu Buttons
    available_menu = st.session_state.session_manager.get_available_menu(st.session_state.session_state_obj)

    if not available_menu:
        st.info("ℹ️ All options viewed. Scroll up in WhatsApp chat to re-read details.")
    else:
        st.markdown("##### 📱 Select an Option (Meta Interactive Quick Replies):")
        formatted_payload = WhatsAppFormatter.format_menu(available_menu)
        
        cols = st.columns(min(len(formatted_payload.options), 3))
        selected_btn = None
        for idx, option_text in enumerate(formatted_payload.options):
            col = cols[idx % min(len(formatted_payload.options), 3)]
            if col.button(f"👉 {option_text}", key=f"wa_btn_{idx}_{option_text}"):
                selected_btn = option_text

        text_input = st.chat_input("Type a message or menu number...")
        user_choice = selected_btn or text_input

        if user_choice:
            if not st.session_state.rate_limiter.is_allowed(st.session_state.user_phone):
                st.error("⚠️ Rate limit reached (Max 15 req/min). Please wait a moment.")
            else:
                now_str = get_current_ist().strftime("%I:%M %p")
                st.session_state.chat_history.append({
                    "sender": "user",
                    "text": user_choice,
                    "time": now_str
                })
                
                # OTP Verification check
                if st.session_state.session_state_obj.otp_code and not st.session_state.session_state_obj.is_authenticated:
                    if user_choice.strip() == st.session_state.session_state_obj.otp_code:
                        st.session_state.session_state_obj.is_authenticated = True
                        reply_text = "✅ *MOBILE VERIFIED!*\nInstant pay-at-clinic slots unlocked. Tap '📅 Book Appointment (Instant Lock)' to reserve."
                    else:
                        reply_text = f"❌ Invalid OTP code. Please enter **{st.session_state.session_state_obj.otp_code}** to authenticate."
                else:
                    command_res = sandwich_engine.process_patient_input(user_choice)
                    reply_text = command_res.message
                
                st.session_state.chat_history.append({
                    "sender": "assistant",
                    "text": reply_text,
                    "time": now_str
                })
                st.rerun()

# ==========================================
# TAB 2: DOCTOR COMMAND CENTER
# ==========================================
with tab_doctor:
    st.title("👨‍⚕️ Doctor Command Center (Dr. Chinmay Hudedamani, MDS)")

    if st.session_state.active_tier == SaaSPlanTier.TIER_1:
        st.markdown(
            """
            <div class="lock-card">
                <h3>🔒 Tier 2 Pro Upgrade Required</h3>
                <p>Doctor Command Center and Emergency OT Reschedule tools require Tier 2 (Pro), Tier 2.5 (Beta), or Tier 3 (Enterprise).</p>
            </div>
            """,
            unsafe_allow_html=True
        )
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
            submit = st.form_submit_button("⚡ Issue Proactive Reschedule Alerts")

            if submit:
                st.success(f"✅ Proactive alerts dispatched to patients for slot '{affected_slot}'. Reason logged: '{custom_reason}'. Time logged: {format_ist_time(get_current_ist())}.")

# ==========================================
# TAB 3: RECEPTIONIST DASHBOARD
# ==========================================
with tab_reception:
    st.title("👩‍💼 Receptionist Operations Desk")

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
        st.subheader("⚡ Offline-First Check-In & On-the-Spot Desk Payment Collector")
        
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
