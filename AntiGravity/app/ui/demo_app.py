# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Clinic Concierge ("Copus") — Pixel-Perfect WhatsApp Web Simulator & Pitch Demo Hub

import streamlit as st
import sys
from pathlib import Path

# Ensure workspace root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

try:
    from app.services.session.session_context import SessionContextManager
    from app.services.session.models import SaaSPlanTier, ActionType, PatientSession
    from app.services.whatsapp_formatter import WhatsAppFormatter
    from app.services.ai_sandwich import AISandwichEngine
    from app.services.security import RateLimiter
    from app.ui.reception_cache import ReceptionistDailyCache, OfflineAppointmentRecord
    from app.utils.time_utils import get_current_ist, format_ist_time
except Exception as err:
    # Graceful fallback imports for zero-crash guarantee
    from app.services.tier_config import SaaSPlanTier
    from app.utils.time_utils import get_current_ist, format_ist_time

# Page Configuration
st.set_page_config(
    page_title="Kasthuri Dental Clinic — WhatsApp AI Concierge",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PIXEL-PERFECT WHATSAPP WEB CSS STYLING ---
WHATSAPP_PITCH_CSS = """
<style>
    /* Main Streamlit App Overrides */
    .stApp {
        background-color: #efeae2 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }
    
    /* WhatsApp Header Bar */
    .wa-pitch-header {
        background-color: #075e54;
        color: #ffffff;
        padding: 14px 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-radius: 10px 10px 0 0;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);
        margin-bottom: 12px;
    }
    .wa-avatar {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background-color: #ffffff;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        margin-right: 12px;
    }
    .wa-clinic-title {
        font-size: 17px;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
    }
    .wa-status-online {
        font-size: 12px;
        color: #25d366;
        font-weight: 600;
    }
    .wa-verified {
        color: #34b7f1;
        font-size: 14px;
    }

    /* WhatsApp Custom Message Bubbles */
    .wa-bubble-user {
        background-color: #d9fdd3;
        color: #111b21;
        padding: 10px 14px;
        border-radius: 8px 8px 0px 8px;
        max-width: 75%;
        margin-left: auto;
        margin-top: 6px;
        margin-bottom: 6px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.12);
        font-size: 14.5px;
        line-height: 1.45;
        position: relative;
    }
    .wa-bubble-bot {
        background-color: #ffffff;
        color: #111b21;
        padding: 10px 14px;
        border-radius: 8px 8px 8px 0px;
        max-width: 80%;
        margin-right: auto;
        margin-top: 6px;
        margin-bottom: 6px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.12);
        font-size: 14.5px;
        line-height: 1.45;
        position: relative;
    }
    .wa-time {
        font-size: 10.5px;
        color: #667781;
        float: right;
        margin-top: 4px;
        margin-left: 8px;
    }
    .wa-blue-ticks {
        color: #53bdeb;
        font-weight: bold;
        font-size: 12px;
    }

    /* Meta Interactive Action Buttons */
    .stButton > button {
        background-color: #ffffff !important;
        color: #00a884 !important;
        border: 1px solid #c0c7d1 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        padding: 10px 16px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08) !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        background-color: #e7f7f3 !important;
        border-color: #00a884 !important;
        color: #075e54 !important;
    }

    /* Admin Cards */
    .lock-banner {
        background-color: #ffffff;
        border-left: 6px solid #ff9800;
        border-radius: 8px;
        padding: 18px;
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        color: #e65100;
    }
    .beta-banner {
        background-color: #fff8e1;
        border-left: 6px solid #f57c00;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 16px;
        color: #e65100;
    }
    .prod-banner {
        background-color: #eef4ff;
        border-left: 6px solid #0F52BA;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 16px;
        color: #0d47a1;
    }
    .badge-tag {
        background-color: #e8f5e9;
        border: 1px solid #66bb6a;
        color: #1b5e20;
        border-radius: 6px;
        padding: 4px 10px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
        margin-right: 6px;
        margin-bottom: 6px;
    }
</style>
"""
st.markdown(WHATSAPP_PITCH_CSS, unsafe_allow_html=True)

# --- ZERO-CRASH STATE INITIALIZATION ---
try:
    if "user_phone" not in st.session_state:
        st.session_state.user_phone = "+919876543210"

    if "active_tier" not in st.session_state:
        st.session_state.active_tier = SaaSPlanTier.TIER_1

    if "session_manager" not in st.session_state:
        st.session_state.session_manager = SessionContextManager()

    if "session_state_obj" not in st.session_state:
        st.session_state.session_state_obj = PatientSession(
            session_id="SESS_WA_PITCH",
            phone_number=st.session_state.user_phone,
            active_tier=st.session_state.active_tier
        )
        st.session_state.session_manager.session_state_obj = st.session_state.session_state_obj

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {
                "sender": "assistant",
                "text": "👋 Welcome to *Kasthuri Dental Clinic*!\nI am Copus, your 24/7 AI Dental Assistant.\n\nHow may we assist you today?",
                "time": get_current_ist().strftime("%I:%M %p IST")
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
        st.session_state.rate_limiter = RateLimiter(max_requests=20, window_seconds=60)

    sandwich_engine = AISandwichEngine(st.session_state.session_manager)

except Exception as init_err:
    st.sidebar.error(f"State Init Fallback: {str(init_err)}")

# --- SIDEBAR ADMIN CONTROLLER ---
st.sidebar.title("⚙️ SaaS Admin Controls")
selected_tier_str = st.sidebar.selectbox(
    "Active SaaS Subscription Plan",
    options=[t.value for t in SaaSPlanTier],
    format_func=lambda x: {
        SaaSPlanTier.TIER_1.value: "🟢 Tier 1: Essential (Menu Bot)",
        SaaSPlanTier.TIER_2.value: "🟡 Tier 2: Pro (Instant Slot Lock + Dual Admin Portals)",
        SaaSPlanTier.TIER_2_5_BETA.value: "🧪 Tier 2.5: Beta Testing (Local NLM + Care Cards Sandbox)",
        SaaSPlanTier.TIER_3.value: "🔴 Tier 3: Enterprise (🚀 In Production - Full AI Sandwich)"
    }[x],
    index=[t.value for t in SaaSPlanTier].index(st.session_state.active_tier.value)
)

# Handle Dynamic Tier Switching
new_tier = SaaSPlanTier(selected_tier_str)
if new_tier != st.session_state.active_tier:
    st.session_state.active_tier = new_tier
    st.session_state.session_state_obj.active_tier = new_tier
    st.session_state.session_manager.set_tier(st.session_state.session_state_obj, new_tier)
    st.rerun()

if st.sidebar.button("🔄 Reset Session History", use_container_width=True):
    try:
        st.session_state.session_state_obj.reset_hidden_options()
        st.session_state.session_state_obj.is_active = True
        st.session_state.session_state_obj.is_authenticated = False
        st.session_state.session_state_obj.check_in_code = None
        st.session_state.chat_history = [
            {
                "sender": "assistant",
                "text": "👋 Welcome to *Kasthuri Dental Clinic*!\nI am Copus, your 24/7 AI Dental Assistant.\n\nHow may we assist you today?",
                "time": get_current_ist().strftime("%I:%M %p IST")
            }
        ]
        st.rerun()
    except Exception as reset_err:
        st.sidebar.error(f"Reset Error: {str(reset_err)}")

st.sidebar.divider()
st.sidebar.subheader("🛡️ Enterprise Defense Status")
st.sidebar.markdown(
    """
    <div>
        <span class="badge-tag">🔒 Distributed Mutex Active</span><br/>
        <span class="badge-tag">🛡️ HMAC SHA-256 Verified</span><br/>
        <span class="badge-tag">⚡ Max Token Bound: 128 chars</span><br/>
        <span class="badge-tag">⏱️ Timezone: Asia/Kolkata (IST)</span>
    </div>
    """,
    unsafe_allow_html=True
)

with st.sidebar.expander("🔍 Session State Inspector"):
    st.write(f"**Phone**: {st.session_state.user_phone}")
    st.write(f"**Active Tier**: {st.session_state.active_tier.value}")
    st.write(f"**Hidden Items**: {list(st.session_state.session_state_obj.hidden_options)}")

# --- MAIN LAYOUT TABS ---
tab_patient, tab_doctor, tab_reception = st.tabs([
    "💬 WhatsApp Patient View",
    "👨‍⚕️ Doctor Command Center",
    "👩‍💼 Receptionist Dashboard"
])

# ==========================================
# TAB 1: WHATSAPP PATIENT VIEW
# ==========================================
with tab_patient:
    
    # Tier Callout Banners
    if st.session_state.active_tier == SaaSPlanTier.TIER_2_5_BETA:
        st.markdown(
            """
            <div class="beta-banner">
                <b>🧪 Tier 2.5 Beta Active</b> | Local NLM Engine & Branch-and-Bound Fallback Enabled.
            </div>
            """,
            unsafe_allow_html=True
        )
    elif st.session_state.active_tier == SaaSPlanTier.TIER_3:
        st.markdown(
            """
            <div class="prod-banner">
                <b>🚀 Enterprise Mode Active (In Production)</b> | Full Gated AI Sandwich Architecture.
            </div>
            """,
            unsafe_allow_html=True
        )

    # WhatsApp Header Bar
    st.markdown(
        f"""
        <div class="wa-pitch-header">
            <div style="display: flex; align-items: center;">
                <div class="wa-avatar">🦷</div>
                <div>
                    <div class="wa-clinic-title">Kasthuri Dental Clinic <span class="wa-verified">☑️</span></div>
                    <div class="wa-status-online">online • Official Business Account</div>
                </div>
            </div>
            <div style="font-size: 13px; font-weight: 600;">{st.session_state.active_tier.value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Render WhatsApp Chat Messages
    for msg in st.session_state.chat_history:
        msg_time = msg.get("time", format_ist_time(get_current_ist()))
        formatted_text = msg["text"].replace("\n", "<br/>")
        
        if msg["sender"] == "user":
            st.markdown(
                f"""
                <div class="wa-bubble-user">
                    {formatted_text}
                    <div class="wa-time">{msg_time} <span class="wa-blue-ticks">✓✓</span></div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div class="wa-bubble-bot">
                    {formatted_text}
                    <div class="wa-time">{msg_time}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.divider()

    # Meta Quick Reply Options
    try:
        available_menu = st.session_state.session_manager.get_available_menu(st.session_state.session_state_obj)
    except Exception:
        available_menu = []

    if not available_menu:
        st.info("ℹ️ All informational choices viewed. Scroll up in WhatsApp to review details.")
    else:
        st.subheader("📱 Select an Option (Meta Interactive Quick Replies):")
        formatted_payload = WhatsAppFormatter.format_menu(available_menu)
        
        cols = st.columns(min(len(formatted_payload.options), 3))
        selected_btn = None
        for idx, option_text in enumerate(formatted_payload.options):
            col = cols[idx % min(len(formatted_payload.options), 3)]
            if col.button(f"👉 {option_text}", key=f"wa_pitch_btn_{idx}_{option_text}"):
                selected_btn = option_text

        # Freeform Chat Input for Tier 2.5 Beta and Tier 3 Enterprise
        user_input = None
        if st.session_state.active_tier in (SaaSPlanTier.TIER_2_5_BETA, SaaSPlanTier.TIER_3):
            user_input = st.chat_input("Type your question or response to Copus AI Concierge...")
        else:
            user_input = st.chat_input("Type menu number or response...")

        user_choice = selected_btn or user_input

        if user_choice:
            try:
                now_ist = format_ist_time(get_current_ist())
                st.session_state.chat_history.append({
                    "sender": "user",
                    "text": user_choice,
                    "time": now_ist
                })
                
                # Multi-Resilient Execution Wrapper
                command_res = sandwich_engine.process_patient_input(user_choice)
                reply_text = command_res.message
                
                st.session_state.chat_history.append({
                    "sender": "assistant",
                    "text": reply_text,
                    "time": now_ist
                })
                st.rerun()
            except Exception as dispatch_err:
                st.error(f"Execution Error: {str(dispatch_err)}")

# ==========================================
# TAB 2: DOCTOR COMMAND CENTER
# ==========================================
with tab_doctor:
    st.title("👨‍⚕️ Doctor Command Center (Dr. Chinmay Hudedamani, MDS)")

    if st.session_state.active_tier == SaaSPlanTier.TIER_1:
        st.markdown(
            """
            <div class="lock-banner">
                <h3>🔒 Tier 2 Pro Upgrade Required</h3>
                <p>The Doctor Command Center, OT Emergency Override Tool, and Schedule Analytics require Tier 2 (Pro), Tier 2.5 (Beta), or Tier 3 (Enterprise).</p>
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
        with st.form("ot_override_form_pitch"):
            affected_slot = st.selectbox("Select OT Slot to Clear", ["11:30 AM – 01:00 PM IST (Surgical)", "03:00 PM – 04:30 PM IST (Implants)"])
            custom_reason = st.text_input("Reason for Override", "Dr. Chinmay called into urgent emergency OT surgery")
            submit = st.form_submit_button("⚡ Issue Reschedule Alerts")

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
            <div class="lock-banner">
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

        if st.button("Verify Patient & Collect Payment", key="pitch_reception_verify"):
            if code_input:
                try:
                    verification = st.session_state.reception_cache.verify_and_collect_payment(code_input, payment_method=pay_method)
                    if verification["status"] == "SUCCESS":
                        st.success(verification["message"])
                    elif verification["status"] == "ALREADY_VERIFIED":
                        st.warning(verification["message"])
                    else:
                        st.error(verification["message"])
                except Exception as rec_err:
                    st.error(f"Verification Error: {str(rec_err)}")
            else:
                st.warning("Please enter a valid 6-character check-in code.")
