# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Clinic Concierge ("Copus") — Hardened Zero-Crash Pitch Demo Hub

import os
import sys
import secrets
from datetime import datetime
from zoneinfo import ZoneInfo

# 1. FIX PYTHON PATH (Prevents White-Screen Import Errors)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st

# 2. MUST BE THE ABSOLUTE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="APEX AI — Copus WhatsApp Concierge",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Strict Indian Standard Time Utility
IST = ZoneInfo("Asia/Kolkata")

def get_ist_time_str() -> str:
    return datetime.now(IST).strftime("%I:%M %p IST")

def get_ist_date_str() -> str:
    return datetime.now(IST).strftime("%d %b %Y, %I:%M %p IST")

# 3. WHATSAPP GLASSMORPHISM & STYLING
CUSTOM_CSS = """
<style>
    /* Global App Background */
    .stApp {
        background-color: #0b141a;
        color: #e9edef;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* WhatsApp Header Bar */
    .wa-header {
        background-color: #202c33;
        padding: 12px 20px;
        border-radius: 10px 10px 0 0;
        border-bottom: 1px solid #222d34;
        display: flex;
        align-items: center;
        margin-bottom: 10px;
    }
    .wa-title {
        font-size: 18px;
        font-weight: 600;
        color: #e9edef;
        margin: 0;
    }
    .wa-subtitle {
        font-size: 12px;
        color: #8696a0;
        margin: 0;
    }
    .online-badge {
        color: #00a884;
        font-size: 12px;
        font-weight: bold;
    }

    /* Cards & Lock Overlays */
    .lock-card {
        background: #111b21;
        border-left: 5px solid #ff9800;
        border-radius: 8px;
        padding: 20px;
        margin: 15px 0;
        color: #e9edef;
    }
    .beta-card {
        background: #111b21;
        border-left: 5px solid #f57c00;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 15px;
        color: #e9edef;
    }
    .production-card {
        background: #111b21;
        border-left: 5px solid #00a884;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 15px;
        color: #e9edef;
    }

    /* Metric Box Customization */
    div[data-testid="stMetricValue"] {
        font-size: 26px;
        font-weight: 700;
        color: #00a884;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# 4. SAFE SESSION STATE INITIALIZATION
if "active_tier" not in st.session_state:
    st.session_state.active_tier = "🟢 Tier 1: Essential"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "sender": "assistant",
            "text": "Hello! I am **Copus**, the Kasthuri Dental Clinic AI assistant.\n\nHow can I assist you with your dental care today?",
            "time": get_ist_time_str()
        }
    ]

if "hidden_options" not in st.session_state:
    st.session_state.hidden_options = set()

if "roster_db" not in st.session_state:
    st.session_state.roster_db = {
        "APX-4928": {"name": "Rahul Kumar", "phone": "+919876543210", "procedure": "Surgical Extraction", "time": "10:30 AM IST", "status": "PENDING_AT_DESK"},
        "APX-8237": {"name": "Priya Sharma", "phone": "+919876543211", "procedure": "Root Canal (RCT)", "time": "11:30 AM IST", "status": "PENDING_AT_DESK"}
    }

# 5. SIDEBAR PITCH CONTROLLER
st.sidebar.title("⚙️ Pitch Admin Control")
selected_tier = st.sidebar.selectbox(
    "Select SaaS Tier Mode:",
    options=[
        "🟢 Tier 1: Essential",
        "🟡 Tier 2: Pro",
        "🧪 Tier 2.5: Beta Testing",
        "🔴 Tier 3: Enterprise (🚀 In Production)"
    ],
    index=0
)

if selected_tier != st.session_state.active_tier:
    st.session_state.active_tier = selected_tier
    st.rerun()

if st.sidebar.button("🔄 Reset Chat Session", use_container_width=True):
    st.session_state.chat_history = [
        {
            "sender": "assistant",
            "text": "Hello! I am **Copus**, the Kasthuri Dental Clinic AI assistant.\n\nHow can I assist you with your dental care today?",
            "time": get_ist_time_str()
        }
    ]
    st.session_state.hidden_options = set()
    st.rerun()

with st.sidebar.expander("🔍 Session State Inspector"):
    st.write(f"**Active Tier**: {st.session_state.active_tier}")
    st.write(f"**Timezone**: `Asia/Kolkata` (IST)")
    st.write(f"**Hidden Options**: {list(st.session_state.hidden_options)}")

# 6. MAIN APPLICATION TABS
tab_patient, tab_doctor, tab_reception = st.tabs([
    "💬 WhatsApp Patient View",
    "👨‍⚕️ Doctor Command Center",
    "👩‍💼 Receptionist Dashboard"
])

# ==========================================
# TAB 1: WHATSAPP PATIENT VIEW
# ==========================================
with tab_patient:
    # Header Banner
    st.markdown(
        """
        <div class="wa-header">
            <div>
                <div class="wa-title">Kasthuri Dental Clinic <span class="online-badge">✔ Verified</span></div>
                <div class="wa-subtitle">Copus AI Concierge • <span style="color:#00a884;">Online</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Tier Callout Banners
    if "Tier 2.5" in st.session_state.active_tier:
        st.markdown(
            """
            <div class="beta-card">
                <b>🧪 Tier 2.5 Sandbox Active</b> — Testing Local NLM Machine Learning & Branch-and-Bound Fallback.
            </div>
            """,
            unsafe_allow_html=True
        )
    elif "Tier 3" in st.session_state.active_tier:
        st.markdown(
            """
            <div class="production-card">
                <b>🚀 Enterprise Mode Active (In Production)</b> — Multi-Branch Auto-Router, TPA Insurance Desk & Gated AI Sandwich.
            </div>
            """,
            unsafe_allow_html=True
        )

    # Render Chat Log
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["sender"]):
            st.markdown(msg["text"])
            st.caption(f"<sub>{msg['time']}</sub>", unsafe_allow_html=True)

    st.divider()

    # Dynamic Menu Options Based on Active Tier
    master_options = [
        "1. Doctor Details & Clinic Timings",
        "2. Cost Ranges & Pricing Sheet",
        "3. 📅 Book Appointment (Instant Lock)",
        "4. ⭐ Patient Reviews",
        "5. 🚨 Emergency Triage"
    ]

    if "Tier 2.5" in st.session_state.active_tier:
        master_options.insert(3, "🩺 🧪 Guided Pre-Triage Tree (Beta)")
        master_options.insert(4, "📋 🧪 Digital Care Cards (Beta)")
    elif "Tier 3" in st.session_state.active_tier:
        master_options.insert(3, "📍 Select Clinic Branch (Multi-Node)")
        master_options.insert(4, "🏥 Cashless TPA Insurance Desk")

    # Filter out read-once options
    available_options = [opt for opt in master_options if opt not in st.session_state.hidden_options]

    # Freeform Input for Tiers 2.5 and 3
    if "Tier 2.5" in st.session_state.active_tier or "Tier 3" in st.session_state.active_tier:
        user_input = st.chat_input("Type your message to Copus AI Concierge...")
        if user_input:
            st.session_state.chat_history.append({"sender": "user", "text": user_input, "time": get_ist_time_str()})
            
            # Simulated Response Logic
            if any(k in user_input.lower() for k in ["pain", "symptom", "triage", "toothache"]):
                reply = "🩺 *Clinical Pre-Triage Assessment*: Your symptoms suggest moderate inflammation. We recommend booking a priority slot today."
            elif any(k in user_input.lower() for k in ["insurance", "tpa", "claim", "star health"]):
                reply = "🏥 *Cashless TPA Desk*: We support Star Health, HDFC ERGO, and ICICI Lombard. Please bring your policy card to the desk."
            else:
                reply = f"I've received your request: *\"{user_input}\"*. How else can I assist you?"

            st.session_state.chat_history.append({"sender": "assistant", "text": reply, "time": get_ist_time_str()})
            st.rerun()

    # Quick Reply Buttons
    if not available_options:
        st.info("ℹ️ All informational choices viewed. Scroll up in WhatsApp to re-read past details.")
    else:
        st.subheader("📱 Tap an option below:")
        cols = st.columns(min(len(available_options), 3))
        
        for idx, option_text in enumerate(available_options):
            col = cols[idx % min(len(available_options), 3)]
            if col.button(option_text, key=f"btn_{idx}_{option_text}"):
                # Add user click
                st.session_state.chat_history.append({"sender": "user", "text": option_text, "time": get_ist_time_str()})

                # Handle Response
                if "Doctor Details" in option_text:
                    st.session_state.hidden_options.add(option_text)
                    reply = "👨‍⚕️ **Lead Surgeon**: Dr. Chinmay Hudedamani (MDS)\n📍 **Location**: Yelahanka Node, Double Road\n🕒 **Hours**: Mon–Sat: 09:00 AM – 08:30 PM IST"
                elif "Cost Ranges" in option_text:
                    st.session_state.hidden_options.add(option_text)
                    reply = "💳 **Pricing Sheet**:\n• Consultation: ₹700\n• Root Canal (RCT): ₹4,500 – ₹7,500\n• Extraction: ₹1,200 – ₹3,500"
                elif "Book Appointment" in option_text:
                    code = f"APX-{secrets.token_hex(2).upper()}"
                    reply = (
                        f"✅ **APPOINTMENT CONFIRMED!**\n\n"
                        f"🎫 **Check-In Code**: `{code}`\n"
                        f"📅 **Booked On**: {get_ist_date_str()}\n"
                        f"💳 **Payment**: **Pay at Clinic Desk** upon arrival (Cash / UPI / Card)\n\n"
                        f"Please show code `{code}` to the receptionist when you arrive."
                    )
                    st.session_state.roster_db[code] = {
                        "name": "Walk-in Patient", "phone": "+919876543210", "procedure": "General Consultation", "time": get_ist_time_str(), "status": "PENDING_AT_DESK"
                    }
                elif "Reviews" in option_text:
                    st.session_state.hidden_options.add(option_text)
                    reply = "⭐ **Patient Reviews**: Rated 4.9/5 stars across 500+ verified visits."
                elif "Emergency" in option_text:
                    reply = "🚨 **Dental Emergency**: Please call our direct duty surgeon immediately:\n📞 tel:+919876543210"
                else:
                    reply = f"Selected: **{option_text}**"

                st.session_state.chat_history.append({"sender": "assistant", "text": reply, "time": get_ist_time_str()})
                st.rerun()

# ==========================================
# TAB 2: DOCTOR COMMAND CENTER
# ==========================================
with tab_doctor:
    st.title("👨‍⚕️ Doctor Command Center (Dr. Chinmay Hudedamani, MDS)")

    if "Tier 1" in st.session_state.active_tier:
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
        col1.metric("Today's Roster", f"{len(st.session_state.roster_db)} Patients")
        col2.metric("Confirmed Check-Ins", "2 Verified")
        col3.metric("Emergency Priority", "1 Acute")
        col4.metric("Revenue Protected", "₹48,500")

        st.divider()
        st.subheader("🚨 Proactive OT Emergency Schedule Override")
        with st.form("ot_override_form"):
            affected_slot = st.selectbox("Select OT Slot to Clear", ["11:30 AM – 01:00 PM IST (Surgical)", "03:00 PM – 04:30 PM IST (Implants)"])
            custom_reason = st.text_input("Reason for Override", "Dr. Chinmay called into urgent OT surgery")
            submit = st.form_submit_button("⚡ Issue Proactive Reschedule Alerts")

            if submit:
                st.success(f"✅ Proactive alerts dispatched to patients for slot '{affected_slot}'. Reason logged: '{custom_reason}'.")

# ==========================================
# TAB 3: RECEPTIONIST DASHBOARD
# ==========================================
with tab_reception:
    st.title("👩‍💼 Receptionist Operations & Waiting-Room Desk")

    if "Tier 1" in st.session_state.active_tier:
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
        st.subheader("⚡ Offline-First Check-In Code & On-the-Spot Payment Collector")
        
        col_in1, col_in2 = st.columns([2, 1])
        with col_in1:
            code_input = st.text_input("Enter Patient Check-In Code (`APX-XXXX`):", placeholder="APX-4928").strip().upper()
        with col_in2:
            pay_method = st.selectbox("Payment Method Collected:", ["UPI (GPay/PhonePe)", "Cash", "Credit/Debit Card"])

        if st.button("Verify Arriving Patient & Collect Payment"):
            if code_input in st.session_state.roster_db:
                record = st.session_state.roster_db[code_input]
                record["status"] = f"PAID_AT_DESK ({pay_method})"
                st.success(
                    f"✅ **CHECK-IN & PAYMENT VERIFIED!**\n\n"
                    f"👤 **Patient**: {record['name']}\n"
                    f"🦷 **Procedure**: {record['procedure']}\n"
                    f"🕒 **Slot**: {record['time']}\n"
                    f"💰 **Status**: Marked as **PAID_AT_DESK** via {pay_method}"
                )
            else:
                st.error(f"❌ Check-in code '{code_input}' not found in today's local roster cache.")

        st.divider()
        st.subheader("📋 Today's Waiting Room Roster")
        for c_code, data in st.session_state.roster_db.items():
            status_color = "🟢" if "PAID" in data["status"] else "🟡"
            st.write(f"{status_color} **`{c_code}`** | {data['name']} | {data['procedure']} | {data['time']} | Status: `{data['status']}`")
