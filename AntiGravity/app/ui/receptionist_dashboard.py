# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI Clinic Receptionist Front-Desk Command Dashboard

import streamlit as st
from datetime import date
from typing import Dict, Any, List

def render_receptionist_dashboard():
    """Renders the Clinic Front-Desk Receptionist Command Dashboard."""
    st.markdown("## 🏥 APEX Dental — Receptionist Command Dashboard")
    st.caption("Live Front-Desk Calendar Ledger, Manual Check-In Overrides & HITL Escalation Feed")

    st.divider()

    # Column Layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📋 Today's Live Calendar Ledger")
        selected_date = st.date_input("Filter Date", date.today())

        # Mock / Demo Ledger Dataset for Streamlit UI
        ledger_data = [
            {
                "time": "10:00 AM",
                "patient": "Rahul Sharma",
                "phone": "+919876543210",
                "code": "APX-4928",
                "status": "CONFIRMED",
                "symptoms": "Throbbing lower right molar toothache preventing sleep",
                "procedure": "Microscopic Single-Sitting Root Canal (RCT)"
            },
            {
                "time": "11:30 AM",
                "patient": "Priya Nair",
                "phone": "+919988776655",
                "code": "APX-8102",
                "status": "SLOT_HELD",
                "symptoms": "Invisalign alignment consult",
                "procedure": "Invisalign® Clear Aligners"
            },
            {
                "time": "02:00 PM",
                "patient": "Vikram Patel",
                "phone": "+919123456789",
                "code": "APX-3391",
                "status": "CHECKED_IN",
                "symptoms": "Wisdom tooth pain",
                "procedure": "Surgical Wisdom Tooth Extraction"
            },
            {
                "time": "04:30 PM",
                "patient": "Ananya Roy",
                "phone": "+919876500000",
                "code": "APX-1120",
                "status": "CANCELLED",
                "symptoms": "Routine dental checkup",
                "procedure": "General Consultation"
            }
        ]

        for item in ledger_data:
            status = item["status"]
            if status == "CONFIRMED":
                status_badge = "🟢 CONFIRMED"
            elif status == "SLOT_HELD":
                status_badge = "🟡 SLOT_HELD (Pending Code)"
            elif status == "CHECKED_IN":
                status_badge = "🔵 CHECKED_IN"
            else:
                status_badge = "🔴 CANCELLED"

            with st.expander(f"⏰ {item['time']} | {item['patient']} ({status_badge})"):
                st.write(f"**Phone:** `{item['phone']}` | **Check-In Code:** `{item['code']}`")
                st.write(f"**Procedure:** {item['procedure']}")
                st.write(f"**Symptoms Reported:** {item['symptoms']}")

                if status in ["CONFIRMED", "SLOT_HELD"]:
                    if st.button(f"Mark CHECKED_IN ({item['code']})", key=f"btn_checkin_{item['code']}"):
                        st.success(f"✅ Patient {item['patient']} (Code: {item['code']}) checked in successfully!")

    with col2:
        st.subheader("⚡ Manual Code Override")
        manual_code = st.text_input("Enter Check-In Code", placeholder="APX-4928").upper()
        if st.button("Verify & Check-In"):
            if manual_code:
                st.success(f"✅ Verified Code '{manual_code}'! Status updated to CHECKED_IN.")
            else:
                st.warning("Please enter a valid check-in code.")

        st.divider()

        st.subheader("🚨 HITL Escalation Feed")
        st.caption("Real-Time Human-In-The-Loop AI Handoff Alerts")

        st.error("🚨 ALERT (10:14 AM): Patient +919876543210 triggered DISTRESSED sentiment ('Severe throbbing pain').")
        if st.button("Take Over Chat (+919876543210)"):
            st.info("💬 Human Receptionist connected to conversation.")

        st.warning("⚠️ ALERT (09:45 AM): LLM Confidence dropped to 0.62 for complex insurance query.")
